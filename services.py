import boto3
import uuid
from os import getenv
from dotenv import load_dotenv
from time import time

load_dotenv()

KEY_ID = getenv("AWS_ACCESS_KEY_ID")
ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
REGION_NAME = getenv("REGION_NAME")

personalize = boto3.client("personalize-runtime",
                           aws_access_key_id=KEY_ID,
                           aws_secret_access_key=ACCESS_KEY,
                           region_name=REGION_NAME)


def get_recommendations_for_user(campaignARN, user_id):
    response = personalize.get_recommendations(
        campaignArn=campaignARN,
        userId=user_id
    )

    recommendations = [item["itemId"] for item in response["itemList"]]

    return recommendations


def get_similar_items(campaignARN, item_id):
    response = personalize.get_recommendations(
        campaignArn=campaignARN,
        itemId=item_id,
        numResults=5
    )

    recommendations = [item["itemId"] for item in response["itemList"]]
    return recommendations


def event_tracker(user_id, item_id):
    personalize_events = boto3.client(service_name="personalize-events",
                                      aws_access_key_id=KEY_ID,
                                      aws_secret_access_key=ACCESS_KEY,
                                      region_name=REGION_NAME
                                      )

    personalize_events.put_events(
        trackingId=getenv("TRACKING_ID"),
        userId=f'{user_id}',
        sessionId= uuid.uuid4().hex,
        eventList=[{
            'sentAt': time(),
            'eventType': 'clicked',
            'itemId': f'{item_id}'
        }]
    )
