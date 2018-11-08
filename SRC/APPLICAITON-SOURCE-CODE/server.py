# This file provided by Facebook is for non-commercial testing and evaluation
# purposes only. Facebook reserves all rights not expressly granted.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# FACEBOOK BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json
import sys
import os
import time
import pymysql
from itertools import izip
from flask import Flask, Response, request

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

@app.route('/api/jobposts', methods=['GET', 'POST'])
def jopposts_handler():
    print "handler"
    conn = pymysql.connect(host='mysqlsrv.cs.tau.ac.il', port=3306, user='DbMysql15', passwd='DbMysql15', db='DbMysql15', autocommit=True)
    cur = conn.cursor()
    if request.method == 'GET':
        print "get";
        get_100_newest_post(cur, get_forms_req({}))
    else:
        print "post";
        get_posts_from_query(request.data, cur)
    returnedList = MySqlToJson2(cur)
    cur.close()
    conn.close()
    returnedList = [{k: str(v) for k, v in jobpost.items()} for jobpost in returnedList]
    return Response(
        json.dumps(returnedList),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )


def get_100_newest_post(cur, formsReq):
    print formsReq
    q= ("SELECT JobPost.post_story_id, JobPost.publish_date, JobPost.employment_form, JobPost.working_manner, JobPost.email, JobPost.full_post_body, Groups.group_name, Groups.group_fb_id, Companies.company_name, Cities.city_name, States.state_name " +
        "FROM JobPost, JobPostGroup, Groups, JobPostCompany, Companies, JobPostCity, Cities, JobPostState, States " +
        "WHERE JobPost.post_id = JobPostGroup.post_id AND JobPost.post_id = JobPostCompany.post_id AND JobPost.post_id = JobPostCity.post_id AND JobPost.post_id = JobPostState.post_id AND JobPostGroup.group_id = Groups.group_id AND JobPostCompany.company_id = Companies.company_id AND JobPostCity.city_id = Cities.city_id AND JobPostState.state_id = States.state_id AND JobPost.employment_form IN " + formsReq +  " ORDER BY publish_date DESC LIMIT 100")
    print q
    cur.execute(q)

def get_forms_req(itemQuery):
    if 'jobtypes' not in itemQuery:
        return "(0 , 1, 2)"
    else:
        return array_to_query_string(itemQuery['jobtypes'])

def get_posts_from_query(itemQuery, cur):
    itemQuery = json.loads(itemQuery)
    innerSqlReq = []
    innerSql_WO_Req = []
    innerSqlOrder = []
    keywords = itemQuery['keywords'] if 'keywords' in itemQuery else ""
    keywords = keywords.lower().split()
    #no search criteria or only keywords
    forms = get_forms_req(itemQuery)
    print "forms" + forms
    if 'states' not in itemQuery and 'cities' not in itemQuery and 'companies' not in itemQuery:
        if 'keywords' in itemQuery:
            search_only_keywords(keywords, cur)
        else:
            get_100_newest_post(cur, forms);
        return
    if 'companies' in itemQuery:
        innerSqlReq.append(get_companies_query(itemQuery['companies']))
    else:
        q = (
            "SELECT post_id, company_name FROM JobPostCompany " +
            "LEFT JOIN Companies " +
            "ON JobPostCompany.company_id = Companies.company_id"
            )
        innerSql_WO_Req.append(q)
    if 'cities' in itemQuery:
        innerSqlReq.append(get_cities_query(itemQuery['cities']))
    else:
        q = ("SELECT post_id, city_name FROM JobPostCity " +
        "LEFT JOIN Cities " +
        "ON JobPostCity.city_id = Cities.city_id")
        innerSql_WO_Req.append(q)
    if 'states' in itemQuery:
        innerSqlReq.append(get_states_query(itemQuery['states']))
    else:
        q = ("SELECT post_id, state_name FROM JobPostState " +
            "LEFT JOIN States " +
            "ON JobPostState.state_id = States.state_id")
        innerSql_WO_Req.append(q)
    joins =  ['JOIN', 'JOIN'] if (len(innerSqlReq) == 2) else ['JOIN', 'LEFT JOIN']
    for innerQuery in innerSqlReq:
        innerSqlOrder.append(innerQuery)
    for innerQuery in innerSql_WO_Req:
        innerSqlOrder.append(innerQuery)
    joinsQuery = "SELECT post_story_id, publish_date, employment_form, working_manner, email, full_post_body, A5.group_name, A5.group_fb_id, company_name, city_name, state_name FROM ("
    joinsQuery += innerSqlOrder[0] + ") AS A1 "+joins[0]+" ("
    joinsQuery += innerSqlOrder[1] + ") AS A2 ON A1.post_id = A2.post_id "+joins[1]+" (" + innerSqlOrder[2]
    joinsQuery += ") AS A3 ON A1.post_id = A3.post_id "
    joinsQuery += "LEFT JOIN JobPost AS A4 ON A1.post_id = A4.post_id "
    joinsQuery += "LEFT JOIN (SELECT  post_id, group_fb_id, group_name FROM Groups, JobPostGroup WHERE Groups.group_id = JobPostGroup.group_id ) AS A5 ON A1.post_id = A5.post_id "
    joinsQuery += "WHERE A4.employment_form IN " + forms +  " ORDER BY A4.publish_date DESC LIMIT 100"
    print joinsQuery
    cur.execute(joinsQuery)

def array_to_query_string(array):
    concated = ""
    for word in array:
        concated += (str(word) + ", ")
    concated = concated[0:len(concated) - 2]
    return '(' + concated + ')'

def get_companies_query(companies_ids):
    companiesQuery = array_to_query_string(companies_ids)
    print "companiesQuery: " + companiesQuery
    return ("SELECT post_id, company_name FROM JobPostCompany " +
        "LEFT JOIN Companies " +
        "ON JobPostCompany.company_id = Companies.company_id " +
        "WHERE Companies.company_id IN " + companiesQuery)

def get_cities_query(cities_ids):
    citisQuery = array_to_query_string(cities_ids)
    print "citisQuery: " + citisQuery
    return ("SELECT post_id, city_name FROM JobPostCity " +
        "LEFT JOIN Cities " +
        "ON JobPostCity.city_id = Cities.city_id " +
        "WHERE Cities.city_id IN " + citisQuery)

def get_states_query(state_ids):
    statesQuery = array_to_query_string(state_ids)
    print "statesQuery: " + statesQuery
    return ("SELECT post_id, state_name FROM JobPostState " +
    "LEFT JOIN States " +
    "ON JobPostState.state_id = States.state_id " +
    "WHERE States.state_id IN " + statesQuery)


def search_only_keywords(words, cur):
    concated = ""
    for word in words:
        concated += ("+" + word + " ")
    concated = concated[0:len(concated) - 1]
    query = "SELECT JobPost.post_story_id, JobPost.publish_date, JobPost.employment_form, JobPost.working_manner, JobPost.email, JobPost.full_post_body, Groups.group_name, Groups.group_fb_id, Companies.company_name, Cities.city_name, States.state_name FROM JobPost, JobPostGroup, Groups, JobPostCompany, Companies, JobPostCity, Cities, JobPostState, States WHERE MATCH(full_post_body) AGAINST('" + concated + "' IN BOOLEAN MODE) AND JobPost.post_id = JobPostGroup.post_id AND JobPost.post_id = JobPostCompany.post_id AND JobPost.post_id = JobPostCity.post_id AND JobPost.post_id = JobPostState.post_id AND JobPostGroup.group_id = Groups.group_id AND JobPostCompany.company_id = Companies.company_id AND JobPostCity.city_id = Cities.city_id AND JobPostState.state_id = States.state_id AND JobPost.employment_form IN (1, 2, 3) ORDER BY publish_date LIMIT 100"
    cur.execute(query)

@app.route('/api/companies', methods=['GET', 'POST'])
def companies_handler():
    return static_handler('Companies', 'company_name')

@app.route('/api/cities', methods=['Get','POST'])
def cities_handler():
    return static_handler('Cities', 'city_name')

@app.route('/api/states', methods=['GET', 'POST'])
def states_handler():
    return static_handler('States', 'state_name')

def static_handler(tableName, name_column):
    conn = pymysql.connect(host='mysqlsrv.cs.tau.ac.il', port=3306, user='DbMysql15', passwd='DbMysql15', db='DbMysql15', autocommit=True)
    cur = conn.cursor()
    if request.method == 'POST':
        itemsQuery = request.data['q'].lower()
    else:
        itemsQuery = request.args['q'].lower()
    #get city list from DB
    cur.execute("SELECT * FROM " + tableName.title()+ " WHERE " + name_column + " Like '" + itemsQuery + "%'")
    returnedList = [];
    for row in cur:
        returnedList.append({'id': row[0], 'name': row[1]})
    cur.close()
    conn.close()
    return Response(
        json.dumps(returnedList),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )

def MySqlToJson2(cursor):
    rows = []
    for row in cursor:
        dict1 = {}
        dict1['post_story_id'] = str(row[0])
        dict1['publish_date'] = str(row[1])
        dict1['employment_form'] = str(row[2])
        dict1['working_manner'] = str(row[3])
        dict1['email'] = str(row[4])
        dict1['full_post_body'] = str(row[5])
        dict1['group_name'] = str(row[6])
        dict1['group_fb_id'] = str(row[7])
        dict1['company_name'] = str(row[8])
        dict1['city_name'] = str(row[9])
        dict1['state_name'] = str(row[10])
        rows.append(dict1)
    return rows


def MySqlToJson(cursor):
    """Returns all rows from a cursor as a list of dicts"""
    desc = cursor.description
    return [dict(izip([col[0] for col in desc], row)) for row in cursor.fetchall()]

if __name__ == '__main__':
    #switch to run localy
    #app.run(port=int(os.environ.get("PORT", 3000)))
    app.run(host=sys.argv[1],port=int(os.environ.get("PORT",int(sys.argv[2]) )))
