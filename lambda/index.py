# lambda/index.py
import json
import os
import re
import urllib.request
import urllib.error

# APIのURL
API_URL = "https://e4ee-34-71-195-82.ngrok-free.app/generate"

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # Cognitoで認証されたユーザー情報を取得
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])
        
        print("Processing message:", message)
        
        # 会話履歴を使用
        messages = conversation_history.copy()
        
        # ユーザーメッセージを追加
        messages.append({
            "role": "user",
            "content": message
        })
        
        # APIへのリクエストデータを準備 - シンプルにメッセージだけを送信
        request_data = json.dumps({"prompt": message}).encode('utf-8')
        
        # APIリクエストの設定
        req = urllib.request.Request(
            API_URL,
            data=request_data,
            headers={'Content-Type': 'application/json'},
            method="POST"
        )
        
        print(f"Calling API at {API_URL} with POST method")
        
        # APIを呼び出し
        with urllib.request.urlopen(req) as response:
            response_data = response.read()
            response_body = json.loads(response_data)
            print("API response:", json.dumps(response_body, default=str))
        
        # アシスタントの応答を取得 - generated_textフィールドを使用
        assistant_response = response_body.get('generated_text', 
                                              response_body.get('message', 
                                                               response_body.get('response', '応答がありませんでした')))
        
        # アシスタントの応答を会話履歴に追加
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })
        
        # 成功レスポンスの返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }
        
    except Exception as error:
        print("Error:", str(error))
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
