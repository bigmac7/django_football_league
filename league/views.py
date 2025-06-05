# league/views.py
from django.shortcuts import render, get_object_or_404
from .models import Team, Match
from collections import defaultdict
from datetime import date
from django.db.models import Q

def league_table(request):
    # Fetch all teams once and store them in a dictionary for easy lookup by name
    all_teams_by_name = {team.name: team for team in Team.objects.all()}

    team_stats = defaultdict(lambda: {
        'played': 0, 'wins': 0, 'draws': 0, 'losses': 0,
        'goals_for': 0, 'goals_against': 0, 'goal_difference': 0, 'points': 0,
        'team_object': None # NEW: Add a placeholder for the actual Team object
    })

    matches = Match.objects.all()

    for match in matches:
        home_team_obj = match.home_team # These are already Team objects
        away_team_obj = match.away_team

        # Get the stats dicts for home and away teams
        home_team_stats = team_stats[home_team_obj.name]
        away_team_stats = team_stats[away_team_obj.name]

        # Assign the actual Team object to the stats dictionary
        home_team_stats['team_object'] = home_team_obj
        away_team_stats['team_object'] = away_team_obj

        # Update played matches
        home_team_stats['played'] += 1
        away_team_stats['played'] += 1

        # Update goals
        home_team_stats['goals_for'] += match.home_score
        home_team_stats['goals_against'] += match.away_score
        away_team_stats['goals_for'] += match.away_score
        away_team_stats['goals_against'] += match.home_score

        # Determine outcome and update points/wins/draws/losses
        if match.home_score > match.away_score:
            home_team_stats['wins'] += 1
            home_team_stats['points'] += 3
            away_team_stats['losses'] += 1
        elif match.home_score < match.away_score:
            away_team_stats['wins'] += 1
            away_team_stats['points'] += 3
            home_team_stats['losses'] += 1
        else:
            home_team_stats['draws'] += 1
            away_team_stats['draws'] += 1
            home_team_stats['points'] += 1
            away_team_stats['points'] += 1

    # Calculate goal difference after all matches processed
    for team_name_str, stats in team_stats.items(): # Iterating through the defaultdict's items
        stats['goal_difference'] = stats['goals_for'] - stats['goals_against']

    # Convert defaultdict values (the stats dictionaries) to a list for sorting
    sorted_table = []
    for team_name_str, stats_dict in team_stats.items():
        # Ensure we're adding the actual Team object and its calculated stats
        sorted_table.append({
            'team_object': stats_dict['team_object'], # Access the stored Team object
            'team_name_str': team_name_str, # Keep the string name for display
            **stats_dict # Unpack all other stats (played, points, etc.)
        })

    # Sort the table:
    sorted_table.sort(key=lambda x: (
        x['points'],
        x['goal_difference'],
        x['goals_for'],
        x['team_name_str'] # Use the string name for tie-breaker if needed
    ), reverse=True)

    recent_fixtures = Match.objects.all().order_by('-match_date')[:5]

    context = {
        'league_table': sorted_table,
        'recent_fixtures': recent_fixtures,
    }
    return render(request, 'league_table.html', context)

def team_detail(request, team_id):
    # Change query back to pk=team_id
    team = get_object_or_404(Team, pk=team_id)

    all_team_matches = Match.objects.filter(
        Q(home_team=team) | Q(away_team=team)
    ).order_by('-match_date')

    today = date.today()
    results = []
    fixtures = []

    for match in all_team_matches:
        if match.match_date <= today:
            results.append(match)
        else:
            fixtures.append(match)

    fixtures.sort(key=lambda x: x.match_date)

    all_teams_in_league = Team.objects.exclude(pk=team.pk)

    # Note: The played_opponents logic using `set`s will still work fine with Team objects
    # as they are hashable. No specific changes needed here related to ID vs slug directly.
    played_opponents_home = set(m.away_team for m in team.home_matches.all())
    played_opponents_away = set(m.home_team for m in team.away_matches.all())

    played_opponents = played_opponents_home.union(played_opponents_away)

    unplayed_home_fixtures = []
    unplayed_away_fixtures = []
    unplayed_both_fixtures = []

    for opponent in all_teams_in_league:
        if opponent not in played_opponents_home:
            unplayed_home_fixtures.append(opponent)

        if opponent not in played_opponents_away:
            unplayed_away_fixtures.append(opponent)

        if opponent not in played_opponents:
            unplayed_both_fixtures.append(opponent)

    context = {
        'team': team,
        'results': results,
        'fixtures': fixtures,
        'unplayed_home_fixtures': unplayed_home_fixtures,
        'unplayed_away_fixtures': unplayed_away_fixtures,
        'unplayed_both_fixtures': unplayed_both_fixtures,
    }
    return render(request, 'team_detail.html', context)