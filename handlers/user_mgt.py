import aiohttp_jinja2
from aiohttp import web
from database import *
from aiohttp_session import get_session
from db_auth import check_password_hash, generate_password_hash
from aiohttp_security import (
    remember, forget, authorized_userid,
    check_permission, check_authorized,
)


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
    session = await get_session(request)
    username = session['username']
    return {'username': username, 'users': users_list, 'title': 'Users'}


async def user_delete(request):
    user_id = request.match_info['id']

    q = User.delete().where(User.id == user_id)
    q.execute()
    raise web.HTTPFound('/users')


@aiohttp_jinja2.template('user_mgt/admin_user_edit.html')
async def admin_user_edit(request):
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

    if user.userpermissions.count() > 0:
        for i, p in enumerate(user.userpermissions):
            if i == 3:
                break
            perms.__setitem__(i, {'perm_id': p.perm_id.id, 'perm_name': p.perm_id.name})

    user_selected.__setitem__('user_perms', perms)

    permissions = Permissions.select()
    perm_list = []
    for pm in permissions:
        perm_list.append({'id': pm.id, 'name': pm.name})

    session = await get_session(request)
    username = session['username']
    return {'username': username, 'user': user_selected, 'perm_list': perm_list, 'title': 'User Edit'}


async def admin_user_edit_post(request):
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

        response = aiohttp_jinja2.render_template('admin_user_edit.html', request, {'user': data, 'perm_list': perm_list})
        # response.headers['Content-Language'] = 'en'
        return response


@aiohttp_jinja2.template('user_mgt/user_profile.html')
async def user_profile(request):

    user_id = await authorized_userid(request)
    user = User.get(User.id == user_id)

    perms = [{'perm_id': '', 'perm_name': ''}, {'perm_id': '', 'perm_name': ''}]
    user_selected = {}

    user_selected.__setitem__('id', user.id)
    user_selected.__setitem__('fname', user.fname)
    user_selected.__setitem__('lname', user.lname)
    user_selected.__setitem__('email', user.email)
    user_selected.__setitem__('disabled', user.disabled)
    user_selected.__setitem__('superuser', user.is_superuser)

    if user.userpermissions.count() > 0:
        for i, p in enumerate(user.userpermissions):
            if i == 3:
                break
            perms.__setitem__(i, {'perm_id': p.perm_id.id, 'perm_name': p.perm_id.name})

    user_selected.__setitem__('user_perms', perms)

    session = await get_session(request)
    username = session['username']
    return {'username': username, 'user': user_selected, 'title': 'My Account'}


@aiohttp_jinja2.template('user_mgt/change_password.html')
async def change_password(request):
    user_id = request.match_info['id']
    session = await get_session(request)
    username = session['username']
    return {'username': username, 'user_id': user_id, 'title': 'Reset Password'}


async def change_password_post(request):
    data = await request.post()
    if 'password' and 'confirm_password' and 'old_password' in data:

        if data['password'] == data['confirm_password']:
            user_id = await authorized_userid(request)
            try:
                user = User.get(User.id == user_id)
                if check_password_hash(data['old_password'], user.passwd):
                    user.passwd = generate_password_hash(data['password'])
                    user.save()
                    raise web.HTTPFound('/user_profile')
                else:
                    return web.Response(status=404)

            except User.DoesNotExist:
                return web.Response(status=404)
        else:
            return web.Response(status=400, text='Bad request')
    else:
        return web.Response(status=404)


@aiohttp_jinja2.template('user_mgt/user_edit.html')
async def user_edit(request):
    user_id = await authorized_userid(request)

    try:
        user = User.get(User.id == user_id)
        user_selected = {}

        user_selected.__setitem__('fname', user.fname)
        user_selected.__setitem__('lname', user.lname)
        user_selected.__setitem__('email', user.email)

        session = await get_session(request)
        username = session['username']
        return {'username': username, 'user': user_selected, 'title': 'Edit Details'}
    except User.DoesNotExist:
        return web.Response(status=404)


async def user_edit_post(request):
    data = await request.post()

    if 'fname' and 'lname' and 'email' in data:
        try:
            user_id = await authorized_userid(request)
            user = User.get(User.id == user_id)
            user.fname = data['fname']
            user.lname = data['lname']
            user.email = data['email']
            user.save()

            # Cannot update email with code below.
            # user.update(fname=data['fname'], lname=data['lname'], email=data['email']).execute()
            
            raise web.HTTPFound('/user_profile')
        except User.DoesNotExist:
            return web.Response(status=404)
    else:
        return web.Response(text='Bad request', status=400)


def setup_user_mgt_routes(app):
    app.add_routes([
        web.get('/users', users_index, name='users'),
        web.get('/user_profile', user_profile, name='user_profile'),
        web.get('/user_delete/{id}', user_delete, name='user_delete'),
        web.get('/admin_user_edit/{id}', admin_user_edit, name='admin_user_edit'),
        web.post('/admin_user_edit_post', admin_user_edit_post, name='admin_user_edit_post'),
        web.get('/user_edit', user_edit, name='user_edit'),
        web.post('/user_edit_post', user_edit_post, name='user_edit_post'),
        web.get('/change_password/{id}', change_password, name='change_password'),
        web.post('/change_password_post', change_password_post, name='change_password_post'),
    ])

