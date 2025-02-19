import calendar
import pytz
from datetime import date
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from modeltrans.fields import TranslationField
from wagtail.admin.edit_handlers import FieldPanel

from .enums import TimeResolution, EmissionUnit


LOCAL_TZ = pytz.timezone(settings.TIME_ZONE)


class EmissionBudgetLevel(models.Model):
    identifier = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    carbon_footprint = models.FloatField(
        verbose_name=_('Maximum emission amount'),
        help_text=_('Amount of carbon emissions per resident per year (in kgs of CO2e.) to reach this level'),
    )
    year = models.PositiveIntegerField(
        verbose_name=_('Year'),
        help_text=_('Year to which this level applies')
    )

    i18n = TranslationField(fields=('name',))

    panels = [
        FieldPanel('identifier'),
        FieldPanel('name'),
        FieldPanel('carbon_footprint'),
        FieldPanel('year'),
    ]

    class Meta:
        verbose_name = _('Emission budget level')
        verbose_name_plural = _('Emission budget levels')
        unique_together = (('identifier', 'year'),)
        ordering = ('year', 'carbon_footprint',)

    def calculate_for_date(
        self, date: date, time_resolution: TimeResolution,
        units: EmissionUnit = EmissionUnit.KG
    ) -> float:
        assert date.year == self.year
        amount = self.carbon_footprint
        days_in_year = 365 if not calendar.isleap(date.year) else 366
        if time_resolution == TimeResolution.YEAR:
            pass
        elif time_resolution == TimeResolution.MONTH:
            days_in_month = calendar.monthrange(date.year, date.month)[1]
            amount = amount / days_in_year * days_in_month
        elif time_resolution == TimeResolution.WEEK:
            amount = amount / days_in_year * 7
        elif time_resolution == TimeResolution.DAY:
            amount = amount / days_in_year
        else:
            raise Exception('Invalid time resolution')
        if units == EmissionUnit.G:
            amount *= 1000
        return amount

    def __str__(self):
        return '%s [%d]' % (self.name, self.year)


class DeviceDailyCarbonFootprint(models.Model):
    device = models.ForeignKey(
        'trips.Device', on_delete=models.CASCADE, related_name='daily_carbon_footprints'
    )
    date = models.DateField()
    carbon_footprint = models.FloatField(help_text=_('Carbon footprint in kg CO2e'))
    average_footprint_used = models.BooleanField(default=False)

    class Meta:
        ordering = ('device', 'date',)
        unique_together = (('device', 'date'),)

    def __str__(self):
        return '%s: %s (%.1f kg)' % (str(self.device), self.date.isoformat(), self.carbon_footprint)


class Prize(models.Model):
    device = models.ForeignKey('trips.Device', on_delete=models.CASCADE, related_name='prizes')
    budget_level = models.ForeignKey(
        EmissionBudgetLevel, blank=True, null=True, on_delete=models.SET_NULL, related_name='prizes'
    )
    prize_month_start = models.DateField(help_text=_("First day of the month for which the prize is awarded"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        year = self.prize_month_start.year
        month = str(self.prize_month_start.month).zfill(2)
        return f'{self.device} [{year}-{month}]: {self.budget_level}'
