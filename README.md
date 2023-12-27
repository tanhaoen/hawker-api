# HawQuer

## What is it?
HawQuer aims to be the most comprehensive, publicly-available API for hawker stall data in Singapore.

Foodie developers rise up!

## Note from the developer
As the Azure SQL database is currently running on the serverless compute tier, expect your first query to be slow or even time out (~1 minute). This is because the serverless database needs time to warm up, so opening the initial connection is slow.

As long as queries are made before the database pauses (if no queries are submitted within 1 hour), subsequent queries should be faster (~500ms).

This is a small project pls help me save money tks

## Getting Started

(proper API documentation on the way~)

GET: https://hawker-api.azurewebsites.net/api/stalls

<u>Parameters</u>
<br>
sort_by (<b>string</b>, <i>optional</i>): field to sort by. <i>Defaults to 'stall_name'</i>.
<br><br>
desc (<b>bool</b>, <i>optional</i>): if true, sort the 'sort_by' field in descending order, otherwise ascending. <i>Defaults to false</i>.
<br><br>
offset (<b>integer</b>, <i>optional</i>): number of records to offset by. <i>Defaults to 0</i>.
<br><br>
limit (<b>integer</b>, <i>optional</i>): limits number of records returned. <i>Defaults to 10</i>.
<br><br>