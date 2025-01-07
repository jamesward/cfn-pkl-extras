import boto3
import cfnresponse
import time

def handler(event, context):
    try:
        if event['RequestType'] in ['Create', 'Update']:
            codebuild = boto3.client('codebuild')

            build = codebuild.start_build(
                projectName=event['ResourceProperties']['ProjectName']
            )

            build_id = build['build']['id']

            # Poll until complete or timeout
            while True:
                # Check remaining lambda execution time
                if context.get_remaining_time_in_millis() < 10000:  # 10 seconds buffer
                    raise Exception("Lambda timeout approaching before build completion")

                response = codebuild.batch_get_builds(ids=[build_id])
                if not response['builds']:
                    raise Exception(f"Build {build_id} not found")

                build_status = response['builds'][0]['buildStatus']

                if build_status == 'SUCCEEDED':
                    response_data = {
                        'BuildId': build_id,
                        'Status': build_status
                    }
                    cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
                    return

                elif build_status in ['FAILED', 'FAULT', 'STOPPED', 'TIMED_OUT']:
                    # Get the build logs URL and failure details
                    logs = response['builds'][0].get('logs', {})
                    log_url = logs.get('deepLink', 'No logs URL available')
                    phase_details = next((phase for phase in response['builds'][0].get('phases', [])
                                          if phase.get('phaseStatus') == 'FAILED'), {})

                    error_message = (
                        f"Build failed with status: {build_status}. "
                        f"Phase: {phase_details.get('phaseType', 'Unknown')}. "
                        f"Error: {phase_details.get('statusMessage', 'No error message available')}. "
                        f"Logs: {log_url}"
                    )

                    response_data = {
                        'BuildId': build_id,
                        'Status': build_status,
                        'Error': error_message
                    }
                    cfnresponse.send(event, context, cfnresponse.FAILED, response_data)
                    return

                # Still in progress, wait before next check
                time.sleep(10)

        elif event['RequestType'] == 'Delete':
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})

    except Exception as e:
        print(f"Error: {str(e)}")
        cfnresponse.send(event, context, cfnresponse.FAILED, {
            'Error': str(e)
        })
