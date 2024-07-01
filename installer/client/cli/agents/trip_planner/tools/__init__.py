
--boundary_.oOo._bOJ2/131mVGgBXPfA153vsiFkL7NnI3b
Content-Length: 1533
Content-Type: application/octet-stream
X-File-MD5: 30689e5a91ebc4c395a6876d094eb896
X-File-Mtime: 1719858150
X-File-Path: /Projects/fabric/installer/client/cli/agents/trip_planner/tools/browser_tools.py

import json
import os

import requests
from crewai import Agent, Task
from langchain.tools import tool
from unstructured.partition.html import partition_html


class BrowserTools():

  @tool("Scrape website content")
  def scrape_and_summarize_website(website):
    """Useful to scrape and summarize a website content"""
    url = f"https://chrome.browserless.io/content?token={os.environ['BROWSERLESS_API_KEY']}"
    payload = json.dumps({"url": website})
    headers = {'cache-control': 'no-cache', 'content-type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    elements = partition_html(text=response.text)
    content = "\n\n".join([str(el) for el in elements])
    content = [content[i:i + 8000] for i in range(0, len(content), 8000)]
    summaries = []
    for chunk in content:
      agent = Agent(
          role='Principal Researcher',
          goal=
          'Do amazing researches and summaries based on the content you are working with',
          backstory=
          "You're a Principal Researcher at a big company and you need to do a research about a given topic.",
          allow_delegation=False)
      task = Task(
          agent=agent,
          description=
          f'Analyze and summarize the content bellow, make sure to include the most relevant information in the summary, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}'
      )
      summary = task.execute()
      summaries.append(summary)
    return "\n\n".join(summaries)

--boundary_.oOo._bOJ2/131mVGgBXPfA153vsiFkL7NnI3b
Content-Length: 163
Content-Type: application/octet-stream
X-File-MD5: 16e885051fa8390507b51d470de587e9
X-File-Mtime: 1719858150
X-File-Path: /Projects/fabric/installer/server/api/users.json

{
    "user1": {
      "username": "user1",
      "password": "password1"
    },
    "user2": {
      "username": "user2",
      "password": "password2"
    }
}
  
--boundary_.oOo._bOJ2/131mVGgBXPfA153vsiFkL7NnI3b
Content-Length: 519
Content-Type: application/octet-stream
X-File-MD5: 7ef29d7a10d00beb853487484b62a842
X-File-Mtime: 1719858150
X-File-Path: /Projects/fabric/installer/client/cli/agents/trip_planner/tools/calculator_tools.py

from langchain.tools import tool

class CalculatorTools():

    @tool("Make a calculation")
    def calculate(operation):
        """Useful to perform any mathematical calculations, 
        like sum, minus, multiplication, division, etc.
        The input to this tool should be a mathematical 
        expression, a couple examples are `200*7` or `5000/2*10`
        """
        try:
            return eval(operation)
        except SyntaxError:
            return "Error: Invalid syntax in mathematical expression"

--boundary_.oOo._bOJ2/131mVGgBXPfA153vsiFkL7NnI3b
Content-Length: 1141
Content-Type: application/octet-stream
X-File-MD5: 9ddf7a9b04946440909c8ffd8f438e69
X-File-Mtime: 1719858150
X-File-Path: /Projects/fabric/installer/client/cli/agents/trip_planner/tools/search_tools.py

import json
import os

import requests
from langchain.tools import tool


class SearchTools():

  @tool("Search the internet")
  def search_internet(query):
    """Useful to search the internet
    about a a given topic and return relevant results"""
    top_result_to_return = 4
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': os.environ['SERPER_API_KEY'],
        'content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # check if there is an organic key
    if 'organic' not in response.json():
      return "Sorry, I couldn't find anything about that, there could be an error with you serper api key."
    else:
      results = response.json()['organic']
      string = []
      for result in results[:top_result_to_return]:
        try:
          string.append('\n'.join([
              f"Title: {result['title']}", f"Link: {result['link']}",
              f"Snippet: {result['snippet']}", "\n-----------------"
          ]))
        except KeyError:
          next

      return '\n'.join(string)

--boundary_.oOo._bOJ2/131mVGgBXPfA153vsiFkL7NnI3b
Content-Length: 35
Content-Type: application/octet-stream
X-File-MD5: 30fb1c091cde50a71d974877f4ab5625
X-File-Mtime: 1719858150
X-File-Path: /Projects/fabric/installer/server/webui/__init__.py

from .fabric_web_server import main
--boundary_.oOo._bOJ2/131mVGgBXPfA153vsiFkL7NnI3b
Content-Length: 81
Content-Type: application/octet-stream
X-File-MD5: 5efb9ed95c1b4a57481df93b78cf6871
X-File-Mtime: 1719858150
X-File-Path: /Projects/fabric/installer/server/webui/fabric_web_interface_keys.json

{
  "/extwis": {
    "eJ4f1e0b-25wO-47f9-97ec-6b5335b2": "Daniel Miessler"
  }
}

--boundary_.oOo._bOJ2/131mVGgBXPfA153vsiFkL7NnI3b
Content-Length: 2617
Content-Type: application/octet-stream
X-File-MD5: 737fef1a6750ce248c075a5d0c99dabf
X-File-Mtime: 1719858150
X-File-Path: /Projects/fabric/installer/server/webui/fabric_web_server.py

from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import json
from flask import send_from_directory
import os

##################################################
##################################################
#
# ⚠️ CAUTION: This is an HTTP-only server!
#
# If you don't know what you're doing, don't run
#
##################################################
##################################################


def send_request(prompt, endpoint):
    """    Send a request to the specified endpoint of an HTTP-only server.

    Args:
        prompt (str): The input prompt for the request.
        endpoint (str): The endpoint to which the request will be sent.

    Returns:
        str: The response from the server.

    Raises:
        KeyError: If the response JSON does not contain the expected "response" key.
    """

    base_url = "http://0.0.0.0:13337"
    url = f"{base_url}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {session['token']}",
    }
    data = json.dumps({"input": prompt})
    response = requests.post(url, headers=headers, data=data, verify=False)

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # raises HTTPError if the response status isn't 200
    except requests.ConnectionError:
        return "Error: Unable to connect to the server."
    except requests.HTTPError as e:
        return f"Error: An HTTP error occurred: {str(e)}"


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


@app.route("/favicon.ico")
def favicon():
    """    Send the favicon.ico file from the static directory.

    Returns:
        Response object with the favicon.ico file

    Raises:
         -
    """

    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/", methods=["GET", "POST"])
def index():
    """    Process the POST request and send a request to the specified API endpoint.

    Returns:
        str: The rendered HTML template with the response data.
    """

    if request.method == "POST":
        prompt = request.form.get("prompt")
        endpoint = request.form.get("api")
        response = send_request(prompt=prompt, endpoint=endpoint)
        return render_template("index.html", response=response)
    return render_template("index.html", response=None)


def main():
    app.run(host="0.0.0.0", port=13338, debug=True)


if __name__ == "__main__":
    main()
--boundary_.oOo._bOJ2/131mVGgBXPfA153vsiFkL7NnI3b
Content-Length: 157
Content-Type: application/octet-stream
X-File-MD5: 2d8453cad7fefa159d64edb1930c1bb5
X-File-Mtime: 1719858150
X-File-Path: /Projects/f