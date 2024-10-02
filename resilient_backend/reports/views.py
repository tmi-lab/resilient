from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from utils.Withings_ScanWatch.Resilient import Resilient
from typing_extensions import Final

import json

@method_decorator(csrf_exempt, name='dispatch')
class WithingsCredentials(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body) # Data tieme status y code 
            # Process the data here
            # For demonstration, we'll just print it and send it back in the response
            print(data)
            print(type(data))
            code = data['code']
            state = data['state']
            user_id = data['userId']
            username = data['username']
            report = Resilient()
            report.create_credentials(code = code, user_uid = user_id, username = username, role = "study-participant")
            return JsonResponse({'status': 'success', 'data': data})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        
        

    def get(self, request, *args, **kwargs):
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@method_decorator(csrf_exempt, name='dispatch')
class ReportGeneration(View):

    def get(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)  # Parse JSON from request body
            report_type = data.get('report_type')  # Get report type from the payload
            participant_number = data.get('participant_number')  # Optional for 'single' report
            
            #Answer from Resilient generation
            report_generator = Resilient()
            report = report_generator.report_generation(report_type = None, user = None)

            return JsonResponse({'status': 'success', 'report': report})
        
        except json.JSONDecodeError:
            
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
        
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

