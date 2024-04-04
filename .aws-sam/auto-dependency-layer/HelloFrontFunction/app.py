import json
import requests
import os
import time


def lambda_handler(event, context):
    STATUS_COLOR = {
        1: "blue",
        2: "yellow",
        3: "gray"
    }
    API_KEY = os.getenv('API_KEY')
    TABLE_ID = os.getenv('TABLE_ID')

    # event["body"] をJSONオブジェクトにデシリアライズ
    print(API_KEY, TABLE_ID, event["body"])
    body = json.loads(event["body"]) if event["body"] else {}

    # Notion APIへのリクエストデータ
    data = {
        "parent": {"type": "database_id", "database_id": TABLE_ID},
        "properties": {
            "タグ": {
                "select": {
                    "name": body["content"]["issueType"].get("name", ""),
                }
            },
            "状態": {
                "type": "status",
                "status": {
                    "name": body["content"]["status"].get("name", ""),
                }
            },
            "タイトル": {
                "title": [{"text": {"content": body["project"].get("projectKey", "") + "-" + str(body["content"].get("key_id", ""))+ "\n" + body["content"].get("summary", "")}}]
            },
            "担当者": {
                "rich_text": [] if body["content"]["assignee"] is None else [{
                    "type": "text",
                    "text": {
                        "content": body["content"]["assignee"].get("name", "")
                    }
                }]
            },
            "優先順位": {
                "select": {
                    "name": body["content"]["priority"].get("name", "")
                }
            },
            "期限": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": "" if body["content"]["dueDate"] is None else body["createdUser"].get("name", "")
                    }
                }],
            },
            "作成者": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": "" if body.get("createdUser") is None else body["createdUser"].get("name", "")
                    }
                }],
            },
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": body.get("content", {}).get("description", "")
                    }
                }
            ]}}
        ]
    }
    # "マイルストーン"プロパティの追加（空のリストでない場合のみ）
    if body["content"].get("milestone") and body["content"]["milestone"]:
        data["properties"]["マイルストーン"] = {
            "select": {
                "name": body["content"]["milestone"][0].get("name", "")
            }
        }

    # Notion APIへのリクエストヘッダー
    headers = {
        'Authorization': 'Bearer ' + API_KEY,
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }

    # Notion APIにデータをPOST
    response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=data)
    print(response.json())

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Successfully created a new page in Notion",
        }),
    }
