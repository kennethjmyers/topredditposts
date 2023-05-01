import redditUtils as ru
import tableDefinition
import praw
import boto3


dynamodb_resource = boto3.resource('dynamodb')


def lambda_handler(event, context):
  # Initializations
  subreddit = "pics"
  cfg_file = ru.findConfig()
  cfg = ru.parseConfig(cfg_file)

  CLIENTID = cfg['CLIENTID']
  CLIENTSECRET = cfg['CLIENTSECRET']
  PASSWORD = cfg['PASSWORD']
  USERNAME = cfg['USERNAME']

  reddit = praw.Reddit(
    client_id=f"{CLIENTID}",
    client_secret=f"{CLIENTSECRET}",
    password=f"{PASSWORD}",
    user_agent=f"Post Extraction (by u/{USERNAME})",
    username=f"{USERNAME}",
  )

  # Get Rising Reddit data
  schema = tableDefinition.schema
  topN = 25
  view = 'rising'
  risingData = ru.getRedditData(reddit=reddit, subreddit=subreddit, view=view, schema=schema, topN=topN)
  risingData = ru.deduplicateRedditData(risingData)

  # Push to DynamoDB
  tableName = view
  risingRawTableDefinition = tableDefinition.getTableDefinition(tableName)
  risingTable = ru.getOrCreateTable(risingRawTableDefinition, dynamodb_resource)
  ru.batchWriter(risingTable, risingData, schema)

  # Get Hot Reddit data
  schema = tableDefinition.schema
  topN = 3
  view = 'hot'
  hotData = ru.getRedditData(reddit=reddit, subreddit=subreddit, view=view, schema=schema, topN=topN)
  hotData = ru.deduplicateRedditData(hotData)

  # Push to DynamoDB
  tableName = view
  hotTableDefinition = tableDefinition.getTableDefinition(tableName)
  hotTable = ru.getOrCreateTable(hotTableDefinition, dynamodb_resource)
  ru.batchWriter(hotTable, hotData, schema)

  return 200
