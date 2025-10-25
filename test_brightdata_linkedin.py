import requests

url = "https://api.brightdata.com/datasets/v3/trigger"
headers = {
    "Authorization": "Bearer 83dcdf1889e1c423fda58acef299d63e5a8325c0a6575edd8cdc390af483830e",
    "Content-Type": "application/json",
}
params = {
    "dataset_id": "gd_lpfll7v5hcqtkxl6l",
    "include_errors": "true",
}
data = [
    {"url": "https://www.linkedin.com/jobs/view/4317860914"},
]

response = requests.post(url, headers=headers, params=params, json=data)
print(response.json())


# call the snapshot endpoint to get the data

url = "https://api.brightdata.com/datasets/v3/snapshot/s_mh6kftr01tbe9jlmgc"
headers = {
    "Authorization": "Bearer 83dcdf1889e1c423fda58acef299d63e5a8325c0a6575edd8cdc390af483830e",
}
params = {
    "format": "json",
}

response = requests.get(url, headers=headers, params=params)
print(response.json())

# https://api.brightdata.com/datasets/v3/snapshot/sd_mh299vd0120owioci5?format=json


# ANnother test

import requests

url = "https://api.brightdata.com/datasets/v3/trigger"
headers = {
    "Authorization": "Bearer 83dcdf1889e1c423fda58acef299d63e5a8325c0a6575edd8cdc390af483830e",
    "Content-Type": "application/json",
}
params = {
    "dataset_id": "gd_lpfll7v5hcqtkxl6l",
    "include_errors": "true",
}
data = [
    {"url": "https://www.linkedin.com/jobs/view/4316780202"},
]

response = requests.post(url, headers=headers, params=params, json=data)
print(response.json())


url = "https://api.brightdata.com/datasets/v3/snapshot/s_mh6k31nn20ly3gehak"
headers = {
    "Authorization": "Bearer 83dcdf1889e1c423fda58acef299d63e5a8325c0a6575edd8cdc390af483830e",
}
params = {
    "format": "json",
}

response = requests.get(url, headers=headers, params=params)
print(response.json())


### Discover endponit. THIS DOES NOT WORK

import requests

url = "https://api.brightdata.com/datasets/v3/trigger"
headers = {
    "Authorization": "Bearer 83dcdf1889e1c423fda58acef299d63e5a8325c0a6575edd8cdc390af483830e",
    "Content-Type": "application/json",
}
params = {
    "dataset_id": "gd_lpfll7v5hcqtkxl6l",
    "include_errors": "true",
    "type": "discover_new",
    "discover_by": "url",
}
data = [
    {"url": "https://www.linkedin.com/jobs/view/4317859825"},
]

response = requests.post(url, headers=headers, params=params, json=data)
print(response.json())

url = "https://api.brightdata.com/datasets/v3/snapshot/sd_mh6jzwix1y214fvkc9"
headers = {
    "Authorization": "Bearer 83dcdf1889e1c423fda58acef299d63e5a8325c0a6575edd8cdc390af483830e",
}
params = {
    "format": "json",
}

response = requests.get(url, headers=headers, params=params)
print(response.json())


### Discover endponit. ANother test

import requests

url = "https://api.brightdata.com/datasets/v3/trigger"
headers = {
    "Authorization": "Bearer 83dcdf1889e1c423fda58acef299d63e5a8325c0a6575edd8cdc390af483830e",
    "Content-Type": "application/json",
}
params = {
    "dataset_id": "gd_lpfll7v5hcqtkxl6l",
    "include_errors": "true",
    "type": "discover_new",
    "discover_by": "url",
}
data = [
    {"url": "https://www.linkedin.com/jobs/view/4316780202"},
]

response = requests.post(url, headers=headers, params=params, json=data)
print(response.json())

url = "https://api.brightdata.com/datasets/v3/snapshot/s_mh6jxpb91p92xtjt1u"
headers = {
    "Authorization": "Bearer 83dcdf1889e1c423fda58acef299d63e5a8325c0a6575edd8cdc390af483830e",
}
params = {
    "format": "json",
}

response = requests.get(url, headers=headers, params=params)

response.content
print(response.json())
