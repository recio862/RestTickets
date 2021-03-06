__author__ = 'rjr862'

from flask import Flask, jsonify, request, abort, redirect
from flask import render_template
from jinja2 import evalcontextfilter, Markup, escape
from app import dbservices, app, authservices, urlservices
import re


@app.route('/projects/<int:project>/tickets', methods=['GET'])
@authservices.get_user_from_session
def get_all_tickets(username, project):
    tckts_dict = dbservices.get_all_tickets(username, project)
    return jsonify(tckts_dict)


@app.route('/projects/', methods=['GET'])
@authservices.get_user_from_session
def get_all_projects(username):
    if not username:
        abort(400)
    prjct_dict = dbservices.get_all_projects(username)
    return jsonify(prjct_dict)

@app.route('/projects/<int:project>/', methods=['GET'])
def get_project(project):
    prjct_dict = dbservices.get_project(project)
    return jsonify(prjct_dict)


@app.route('/projects/<int:project>/', methods=['DELETE'])
@authservices.get_user_from_session
def delete_project(username, project):
    dbservices.delete_project(username, project)
    return ('', 204)


@app.route('/projects/', methods=['DELETE'])
@authservices.get_user_from_session
def delete_projects(username):
    dbservices.delete_projects(username)
    return ('', 204)

@app.route('/projects/<int:project>/tickets/', methods=['DELETE'])
@authservices.get_user_from_session
def delete_tickets(username, project):
    dbservices.delete_tickets(username, project)
    return ('', 204)

@app.route('/projects/<int:project>/tickets/<int:ticket>', methods=['GET'])
def get_ticket(project, ticket):
    tckt_map = dbservices.get_ticket(project, ticket)
    return jsonify(tckt_map)




@app.route('/projects/<int:project>/tickets/<int:ticket>', methods=['DELETE'])
@authservices.get_user_from_session
def delete_ticket(username, project, ticket):
    dbservices.delete_ticket(username, project, ticket)
    return ('', 204)


@app.route('/projects/<int:project>/tickets/', methods=['POST'])
def post_ticket(project):
    if not request.json:
        abort(400)
    if not dbservices.validate_ticket(project, request.json):
        abort(400)

    location = dbservices.post_ticket(project, request.json)
    location = urlservices.get_ticket_url(project, location.get('xhref'))
    location_map = {'location': location}
    return jsonify(location_map), 201, location_map


# @app.route('/projects/', methods=['GET'])
# @authservices.get_user_from_session
# def get_project(username):
#     if not request.json or not username:
#         abort(400)
#     location = dbservices.post_project(request.json, username)
#     location = urlservices.get_project_url(location.get('xhref'))
#     location_dict = {'location': location}
#     return jsonify(location_dict), 201, location_dict

@app.route('/projects/', methods=['POST'])
@authservices.get_user_from_session
def post_project(username):
    if not request.json or not username:
        abort(400)
    location = dbservices.post_project(request.json, username)
    location = urlservices.get_project_url(location.get('xhref'))
    location_dict = {'location': location}
    return jsonify(location_dict), 201, location_dict

@app.route('/projects/<int:project>/', methods=['PUT'])
@authservices.get_user_from_session
def put_project(username, project):
    if not request.json or not username:
        abort(400)
    location = dbservices.put_project(request.json, username, project)
    location = urlservices.get_project_url(project)
    location_dict = {'location': location}
    return jsonify(location_dict), 201, location_dict

@app.route('/projects/<int:project>/tickets/<int:ticket>', methods=['PUT'])
@authservices.get_user_from_session
def put_ticket(username, project, ticket):
    if not request.json or not username:
        abort(400)
    location = dbservices.put_ticket(request.json, username, project, ticket)
    location = urlservices.get_ticket_url(project, ticket)
    location_dict = {'location': location}
    return jsonify(location_dict), 201, location_dict


@app.route('/')
@authservices.authenticate_with_sessionid
def home_page(username):
    if not username:
        return render_template('signin.html')
    else:
        ticket_list = []
        project = dbservices.get_project_for_user(username)
        if project:
            ticket_list = dbservices.get_all_tickets(username, project, type='list')
        return render_template('index2.html', tickets=ticket_list, username=username)

@app.route('/get')
@authservices.authenticate_with_sessionid
def get_page(username):
    if not username:
        return render_template('signin.html')
    else:
        return render_template('get.html', username = username)

@app.route('/post')
@authservices.authenticate_with_sessionid
def post_page(username):
    if not username:
        return render_template('signin.html')
    else:
        return render_template('post.html', username = username)

@app.route('/put')
@authservices.authenticate_with_sessionid
def put_page(username):
    if not username:
        return render_template('signin.html')
    else:
        return render_template('put.html', username = username)

@app.route('/delete')
@authservices.authenticate_with_sessionid
def delete_page(username):
    if not username:
        return render_template('signin.html')
    else:
        return render_template('delete.html' , username = username)

@app.route('/api')
@authservices.authenticate_with_sessionid
def api_page(username):
    if not username:
        return render_template('signin.html')
    else:
        return render_template('api.html', username=username)

@app.route('/about')
@authservices.authenticate_with_sessionid
def about_page(username):
    if not username:
        return render_template('signin.html')
    else:
        return render_template('about.html', username=username)


@app.route('/logout')
@authservices.get_user_from_session
def logout(username):
    if username:
        authservices.remove_user_from_session(username)
    return redirect(urlservices.base_url)


@app.route('/login', methods=['POST'])
@authservices.authenticate_with_form_fields
def user_login_form(username):
    if not username:
        return '0'
    authservices.start_session(username)
    return username


@app.route('/login/auth', methods=['POST'])
@authservices.authenticate_with_auth_header
def user_login_auth(key):
    if not key:
        return '0'
    return key


@app.route('/register', methods=['POST'])
@authservices.validate_new_user
def post_user(request_body):
    if not request_body:
        return '0'
    # return render_template('dashboard.html')
    else:
        dbservices.post_user(request_body)
    print('test')
    return '1'


_paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
                          for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


@app.template_filter()
@evalcontextfilter
def space2nbsp(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace(' ', '&nbsp') \
                          for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result
