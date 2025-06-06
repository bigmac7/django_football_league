# league/views.py
from django.shortcuts import render, get_object_or_404
from .models import Team, Match
from collections import defaultdict
from datetime import date
from django.db.models import Q

# league/views.py
from django.shortcuts import render, get_object_or_404
from .models import Team, Match
# from collections import defaultdict # We'll use a regular dict now for clearer initialization
from datetime import date
from django.db.models import Q

def league_table(request):
    all_teams = Team.objects.all() # Fetch all teams from the database

    # Initialize team_stats as a regular dictionary.
    # This ensures every team has an entry from the start, with zero stats.
    team_stats = {}
    for team_obj in all_teams:
        team_stats[team_obj.name] = {
            'played': 0, 'wins': 0, 'draws': 0, 'losses': 0,
            'goals_for': 0, 'goals_against': 0, 'goal_difference': 0, 'points': 0,
            'team_object': team_obj # Crucially, store the actual Team object here
        }

    matches = Match.objects.all()

    for match in matches:
        home_team_obj = match.home_team
        away_team_obj = match.away_team

        # Access the stats dictionaries for the home and away teams.
        # Use .get() with a default in case a team exists in a match but somehow wasn't in all_teams (unlikely with FKs but safer)
        home_team_stats = team_stats.get(home_team_obj.name)
        away_team_stats = team_stats.get(away_team_obj.name)

        # If for some reason a team in a match wasn't in our initial all_teams list, skip this match.
        if not home_team_stats or not away_team_stats:
            continue

        # The 'team_object' is already stored during initialization, no need to re-assign here.

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
    # Iterate through the values of team_stats, which are the dictionaries containing stats
    for team_name_str, stats_dict in team_stats.items():
        stats_dict['goal_difference'] = stats_dict['goals_for'] - stats_dict['goals_against']

    # Convert the dictionary's values (the stats dictionaries) into a list for sorting
    sorted_table = list(team_stats.values()) # This gets a list of all the stats dictionaries

    # Sort the table:
    # 1. By points (descending)
    # 2. By goal difference (descending)
    # 3. By goals for (descending)
    # 4. By team name (ascending - alphabetical tie-breaker using the Team object's name)
    sorted_table.sort(key=lambda x: (
        x['points'],
        x['goal_difference'],
        x['goals_for'],
        x['team_object'].name # Use the actual Team object's name for sorting
    ), reverse=True) # Reverse for points, GD, GF to be descending

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