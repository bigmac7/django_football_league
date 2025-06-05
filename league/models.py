# league/models.py
from django.db import models
# from django.utils.text import slugify # Remove this import

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # Remove the slug field entirely:
    # slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    # Remove the custom save method:
    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.name)
    #     super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']

class Match(models.Model):
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    match_date = models.DateField(auto_now_add=True) # or DateField(blank=True, null=True) if you want to set it manually

    def __str__(self):
        return f"{self.home_team} {self.home_score}-{self.away_score} {self.away_team}"

    class Meta:
        verbose_name_plural = "Matches"
        ordering = ['-match_date']