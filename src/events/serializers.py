from rest_framework import serializers
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from .models import Event, EventPeriodicTask
import uuid


class CrontabScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrontabSchedule
        fields = ['minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year'] 

class PeriodicTaskSerializer(serializers.ModelSerializer):
    crontab = CrontabScheduleSerializer()  # Include crontab details

    class Meta:
        model = PeriodicTask
        fields = ['name', 'task', 'crontab']
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        event_type = self.context.get('event_type')
        if event_type == 'Daily':
            representation['crontab'] = {
                'minute': instance.crontab.minute,
                'hour': instance.crontab.hour,
                'description': f'every day at {instance.crontab.hour}:{instance.crontab.minute}'
            }
        elif event_type == 'Weekly':
            representation['crontab'] = {
                'minute': instance.crontab.minute,
                'hour': instance.crontab.hour,
                'day_of_week': instance.crontab.day_of_week,
                'description': f'every week on {instance.crontab.day_of_week} at {instance.crontab.hour}:{instance.crontab.minute}'
            }
        elif event_type == 'Monthly':
            representation['crontab'] = {
                'minute': instance.crontab.minute,
                'hour': instance.crontab.hour,
                'day_of_month': instance.crontab.day_of_month,
                'description': f'every month on the {instance.crontab.day_of_month} at {instance.crontab.hour}:{instance.crontab.minute}'
            }
        elif event_type == 'Yearly':
            representation['crontab'] = {
                'minute': instance.crontab.minute,
                'hour': instance.crontab.hour,
                'day_of_month': instance.crontab.day_of_month,
                'month_of_year': instance.crontab.month_of_year,
                'description': f'every year on {instance.crontab.day_of_month} of month {instance.crontab.month_of_year} at {instance.crontab.hour}:{instance.crontab.minute}'
            }

        return representation
        

class EventPeriodicTaskSerializer(serializers.ModelSerializer):
    periodic_task = PeriodicTaskSerializer()

    class Meta:
        model = EventPeriodicTask
        fields = ['periodic_task']
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        event = instance.event  
        representation['periodic_task'] = PeriodicTaskSerializer(
            instance.periodic_task,
            context={'event_type': event.type}
        ).data
        return representation

class EventSerializer(serializers.ModelSerializer):
    periodic_tasks  = EventPeriodicTaskSerializer(many=True,read_only=True)

    start_minute = serializers.CharField(write_only=True, required=True)
    start_hour = serializers.CharField(write_only=True, required=True)
    start_day_of_week = serializers.CharField(write_only=True, required=False, default='*')
    start_day_of_month = serializers.CharField(write_only=True, required=False, default='*')
    start_month_of_year = serializers.CharField(write_only=True, required=False, default='*')

    end_minute = serializers.CharField(write_only=True, required=True)
    end_hour = serializers.CharField(write_only=True, required=True)
    end_day_of_week = serializers.CharField(write_only=True, required=False, default='*')
    end_day_of_month = serializers.CharField(write_only=True, required=False, default='*')
    end_month_of_year = serializers.CharField(write_only=True, required=False, default='*')

    class Meta:
        model = Event
        fields = ('id', 'name', 'description', 'type', 'created', 'modified', 
                  'start_minute', 'start_hour', 'start_day_of_week', 
                  'start_day_of_month', 'start_month_of_year', 'end_minute', 'end_hour', 
                  'end_day_of_week', 'end_day_of_month', 'end_month_of_year','periodic_tasks')
        
        read_only_fields = ('activate','created', 'modified','periodic_tasks')

    def validate(self, data):
        errors = {}
        start_minute = data.get('start_minute')
        start_hour = data.get('start_hour')
        end_minute = data.get('end_minute')
        end_hour = data.get('end_hour')

        if not (0 <= int(start_minute) <= 59):
            errors['start_minute'] = 'Start minute must be between 0 and 59.'
        if not (0 <= int(end_minute) <= 59):
            errors['end_minute'] = 'End minute must be between 0 and 59.'
        if not (0 <= int(start_hour) <= 23):
            errors['start_hour'] = 'Start hour must be between 1 and 24.'
        if not (0 <= int(end_hour) <= 23):
            errors['end_hour'] = 'End hour must be between 1 and 24.'

        # Validate crontab fields
        start_day_of_week = data.get('start_day_of_week', '*')
        start_day_of_month = data.get('start_day_of_month', '*')
        start_month_of_year = data.get('start_month_of_year', '*')
        end_day_of_week = data.get('end_day_of_week', '*')
        end_day_of_month = data.get('end_day_of_month', '*')
        end_month_of_year = data.get('end_month_of_year', '*')

        if start_day_of_week != '*' and not (1 <= int(start_day_of_week) <= 7):
            errors['start_day_of_week'] = 'Start day of week must be between 1 and 7 or "*".'
        if end_day_of_week != '*' and not (1 <= int(end_day_of_week) <= 7):
            errors['end_day_of_week'] = 'End day of week must be between 1 and 7 or "*".'
        if start_day_of_month != '*' and not (1 <= int(start_day_of_month) <= 30):
            errors['start_day_of_month'] = 'Start day of month must be between 1 and 30 or "*".'
        if end_day_of_month != '*' and not (1 <= int(end_day_of_month) <= 30):
            errors['end_day_of_month'] = 'End day of month must be between 1 and 30 or "*".'
        if start_month_of_year != '*' and not (1 <= int(start_month_of_year) <= 12):
            errors['start_month_of_year'] = 'Start month of year must be between 1 and 12 or "*".'
        if end_month_of_year != '*' and not (1 <= int(end_month_of_year) <= 12):
            errors['end_month_of_year'] = 'End month of year must be between 1 and 12 or "*".'

        # Validate event type specific fields
        event_type = data.get('type')

        if event_type == 'Daily':
            if start_day_of_week != '*' or start_day_of_month != '*' or start_month_of_year != '*':
                errors['start_schedule'] = 'For daily events, only minute and hour should be specified.'
            if end_day_of_week != '*' or end_day_of_month != '*' or end_month_of_year != '*':
                errors['end_schedule'] = 'For daily events, only minute and hour should be specified.'

        elif event_type == 'Weekly':
            if start_day_of_month != '*' or start_month_of_year != '*':
                errors['start_schedule'] = 'For weekly events, only minute, hour, and day of week should be specified.'
            if end_day_of_month != '*' or end_month_of_year != '*':
                errors['end_schedule'] = 'For weekly events, only minute, hour, and day of week should be specified.'

        elif event_type == 'Monthly':
            if start_day_of_week != '*' or start_month_of_year != '*':
                errors['start_schedule'] = 'For monthly events, only minute, hour, and day of month should be specified.'
            if end_day_of_week != '*' or end_month_of_year != '*':
                errors['end_schedule'] = 'For monthly events, only minute, hour, and day of month should be specified.'

        elif event_type == 'Yearly':
            if start_day_of_week != '*':
                errors['start_schedule'] = 'For yearly events, only minute, hour, day of month, and month of year should be specified.'
            if end_day_of_week != '*':
                errors['end_schedule'] = 'For yearly events, only minute, hour, day of month, and month of year should be specified.'
        


        if data.get('start_month_of_year') > data.get('end_month_of_year'):
            errors['erore'] = 'erore'
        elif data.get('start_month_of_year') == data.get('end_month_of_year'):
            if data.get('start_day_of_month') > data.get('end_day_of_month'):
                errors['erore'] = 'erore'
            elif data.get('start_day_of_month') == data.get('end_day_of_month'):
                if data.get('start_day_of_week') > data.get('end_day_of_week'):
                    errors['erore'] = 'erore'
                elif data.get('start_day_of_week') == data.get('end_day_of_week'):
                    if data.get('start_hour') > data.get('end_hour'):
                        errors['erore'] = 'erore'
                    elif data.get('start_hour') == data.get('end_hour'):
                        if data.get('start_minute') > data.get('end_minute'):
                            errors['erore'] = 'erore'



        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        start_minute = validated_data.pop('start_minute')
        start_hour = validated_data.pop('start_hour')
        start_day_of_week = validated_data.pop('start_day_of_week', '*')
        start_day_of_month = validated_data.pop('start_day_of_month', '*')
        start_month_of_year = validated_data.pop('start_month_of_year', '*')
        
        end_minute = validated_data.pop('end_minute')
        end_hour = validated_data.pop('end_hour')
        end_day_of_week = validated_data.pop('end_day_of_week', '*')
        end_day_of_month = validated_data.pop('end_day_of_month', '*')
        end_month_of_year = validated_data.pop('end_month_of_year', '*')

        event = Event.objects.create(**validated_data)
        
        start_schedule, created = CrontabSchedule.objects.get_or_create(
            minute=start_minute,
            hour=start_hour,
            day_of_week=start_day_of_week,
            day_of_month=start_day_of_month,
            month_of_year=start_month_of_year,
        )
        
        start_periodic_task = PeriodicTask.objects.create(
            crontab=start_schedule,
            name=f'start_event_{event.id}',
            task='events.tasks.event_activate',
            args=[event.id],   
        )
        
        EventPeriodicTask.objects.create(
            event=event,
            periodic_task=start_periodic_task
        )
        
        end_schedule, created = CrontabSchedule.objects.get_or_create(
            minute=end_minute,
            hour=end_hour,
            day_of_week=end_day_of_week,
            day_of_month=end_day_of_month,
            month_of_year=end_month_of_year,
        )
        
        end_periodic_task = PeriodicTask.objects.create(
            crontab=end_schedule,
            name=f'end_event_{event.id}',
            task='events.tasks.event_deactivate',
            args=[event.id],   
        )
        EventPeriodicTask.objects.create(
            event=event,
            periodic_task=end_periodic_task
        )
        return event
    
