import json
import urllib.request
import urllib.parse
import http.cookiejar
import sys

BASE_URL = "http://127.0.0.1:8000/api"

# Set up a cookie jar to handle session cookies automatically
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

def make_request(path, method="GET", body=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as res:
            res_body = res.read().decode("utf-8")
            status = res.status
            try:
                parsed = json.loads(res_body)
                return status, parsed
            except json.JSONDecodeError:
                return status, res_body
    except urllib.error.HTTPError as e:
        res_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(res_body)
            return e.code, parsed
        except json.JSONDecodeError:
            return e.code, res_body
    except Exception as e:
        return 500, str(e)

def run_tests():
    print("=" * 60)
    print("Starting Step-by-Step API Endpoint Testing")
    print("=" * 60)

    # 1. Register User 1
    print("\n[Step 1] POST /api/register (Register Alice)")
    status, res = make_request("/register", method="POST", body={"username": "alice", "password": "password123"})
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")

    # 2. Register User 2
    print("\n[Step 2] POST /api/register (Register Bob)")
    status, res = make_request("/register", method="POST", body={"username": "bob", "password": "password123"})
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")

    # 3. Try login with incorrect password
    print("\n[Step 3] POST /api/login/ (Fail Login)")
    status, res = make_request("/login/", method="POST", body={"username": "alice", "password": "wrongpassword"})
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")

    # 4. Login User 1 (Alice)
    print("\n[Step 4] POST /api/login/ (Success Login Alice)")
    status, alice_data = make_request("/login/", method="POST", body={"username": "alice", "password": "password123"})
    print(f"Status: {status}")
    print(f"Response: {json.dumps(alice_data, indent=2)}")
    if status != 200:
        print("Login failed, aborting rest of the tests.")
        sys.exit(1)

    # 5. Search users for "bo"
    print("\n[Step 5] GET /api/users/?search=bo")
    status, res = make_request("/users/?search=bo")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")
    
    # Store bob's ID from search results
    bob_id = None
    if isinstance(res, list):
        for u in res:
            if u["username"] == "bob":
                bob_id = u["id"]
                break
    
    if not bob_id:
        print("Could not find Bob's ID from search results, defaulting to guess (2)")
        bob_id = 2

    # 6. Get initial conversations (should be empty)
    print("\n[Step 6] GET /api/conversations/ (Initial - empty)")
    status, res = make_request("/conversations/")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")

    # 7. Start conversation with Bob
    print(f"\n[Step 7] POST /api/conversations/ (Start Chat with Bob ID {bob_id})")
    status, conv_data = make_request("/conversations/", method="POST", body={"recipient_id": bob_id})
    print(f"Status: {status}")
    print(f"Response: {json.dumps(conv_data, indent=2)}")
    conv_id = conv_data.get("id")

    # 8. List conversations again (should contain the new conversation)
    print("\n[Step 8] GET /api/conversations/ (List chats after creation)")
    status, res = make_request("/conversations/")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")

    # 9. Send a text message to Bob
    print(f"\n[Step 9] POST /api/messages/ (Send text message)")
    status, msg_data = make_request("/messages/", method="POST", body={
        "conv_id": conv_id,
        "message_type": "text",
        "content": "Hey Bob! How are you?"
    })
    print(f"Status: {status}")
    print(f"Response: {json.dumps(msg_data, indent=2)}")
    msg_id = msg_data.get("id")

    # 10. Send a game invite to Bob
    print(f"\n[Step 10] POST /api/messages/ (Send game invite)")
    status, res = make_request("/messages/", method="POST", body={
        "conv_id": conv_id,
        "message_type": "games",
        "content": json.dumps({
            "title": "Tic-Tac-Toe",
            "url": "http://localhost:3000/games/tictactoe",
            "desc": "Join me for a game of Tic-Tac-Toe!"
        })
    })
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")

    # 11. Fetch messages history (no cursor)
    print(f"\n[Step 11] GET /api/conversation/{conv_id}/messages/ (Fetch all messages)")
    status, res = make_request(f"/conversation/{conv_id}/messages/")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")

    # 12. Fetch messages history with cursor (after first message)
    print(f"\n[Step 12] GET /api/conversation/{conv_id}/messages/?after={msg_id}")
    status, res = make_request(f"/conversation/{conv_id}/messages/?after={msg_id}")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")

    # 13. Get games catalog
    print("\n[Step 13] GET /api/games")
    status, res = make_request("/games")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(res, indent=2)}")

    print("\n" + "=" * 60)
    print("All Step-by-Step API Tests Completed!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
