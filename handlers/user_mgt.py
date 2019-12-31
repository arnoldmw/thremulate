import aiohttp_jinja2
from aiohttp import web
from database import *


@aiohttp_jinja2.template('user_mgt/users_index.html')
async def users_index(request):
    users = User.select()
    perms = []
    users_list = []
    user = {}
    for m in users:
        user.__setitem__('id', m.id)
        user.__setitem__('fname', m.fname)
        user.__setitem__('lname', m.lname)
        user.__setitem__('email', m.email)
        user.__setitem__('disabled', m.disabled)
        user.__setitem__('superuser', m.is_superuser)

        # for n in m.userpermissions:
        #     perms.append(n.perm_name)
        #
        # user.__setitem__('perms', perms)

        users_list.append(user)
        user = {}
        # perms = []
    return {'users': users_list, 'title': 'Users'}


async def user_delete(request):
    user_id = request.match_info['id']

    q = User.delete().where(User.id == user_id)
    q.execute()
    raise web.HTTPFound('/users')


@aiohttp_jinja2.template('user_mgt/user_edit.html')
async def user_edit(request):
    user_id = request.match_info['id']
    user = User.get(User.id == user_id)
    perms = [{'perm_id': '', 'perm_name': ''}, {'perm_id': '', 'perm_name': ''}]
    user_selected = {}

    user_selected.__setitem__('id', user.id)
    user_selected.__setitem__('fname', user.fname)
    user_selected.__setitem__('lname', user.lname)
    user_selected.__setitem__('email', user.email)
    user_selected.__setitem__('disabled', user.disabled)
    user_selected.__setitem__('superuser', user.is_superuser)

    i = 0
    if user.userpermissions.count() > 0:
        for p in user.userpermissions:
            # perms.append()
            if i == 3:
                break
            perms.__setitem__(i, {'perm_id': p.perm_id.id, 'perm_name': p.perm_id.name})
            # perms.append({'perm_id': p.perm_id.id, 'perm_name': p.perm_id.name})
            i = i + 1

    user_selected.__setitem__('user_perms', perms)

    permissions = Permissions.select()
    perm_list = []
    for pm in permissions:
        perm_list.append({'id': pm.id, 'name': pm.name})

    # print(user_selected)
    # print(perm_list)
    return {'user': user_selected, 'perm_list': perm_list, 'title': 'User Edit'}


async def user_edit_post(request):
    data = await request.post()
    # print('register')
    # for key in data.keys():
    #     print(key + ': ' + data[key])

    permissions = []

    if 'user_id' and 'fname' and 'lname' and 'email' and 'disabled' and 'superuser' in data:

        user_id = data['user_id']

        if 'public' in data:
            permissions.append({'user_id': user_id, 'perm_id': data['public']})
        if 'protected' in data:
            permissions.append({'user_id': user_id, 'perm_id': data['protected']})

        if permissions.__len__() > 0:
            UserPermissions.delete().where(UserPermissions.user_id == user_id).execute()

        if data['disabled'] == 'False':
            disabled = False
        else:
            disabled = True

        if data['superuser'] == 'False':
            superuser = False
        else:
            superuser = True

        UserPermissions.insert_many(permissions).execute()
        User.update(fname=data['fname'], lname=data['lname'], email=data['email'], is_superuser=superuser,
                    disabled=disabled).where(User.id == user_id).execute()

        raise web.HTTPFound('/users')

    else:

        permissions = Permissions.select()
        perm_list = []
        for pm in permissions:
            perm_list.append({'id': pm.id, 'name': pm.name})

        response = aiohttp_jinja2.render_template('user_edit.html', request, {'user': data, 'perm_list': perm_list})
        # response.headers['Content-Language'] = 'en'
        return response


def setup_user_mgt_routes(app):
    app.add_routes([
        web.get('/users', users_index, name='users'),
        web.get('/user_delete/{id}', user_delete, name='user_delete'),
        web.get('/user_edit/{id}', user_edit, name='user_edit'),
        web.post('/user_edit_post', user_edit_post, name='user_edit_post'),
    ])

