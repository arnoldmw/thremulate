import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import (
    check_permission, check_authorized,
)
from aiohttp_session import get_session
from stae.database import *
from stae.db_auth import check_password_hash, generate_password_hash


@aiohttp_jinja2.template('user_mgt/users_index.html')
async def users_index(request):
    """
    Retrieves the template showing all registered users.
    :param request:
    :return: Template with all users otherwise an exception is raised.
    """
    await check_permission(request, 'protected')

    users = User.select()
    users_list = []
    user = {}
    for m in users:
        user.__setitem__('id', m.id)
        user.__setitem__('fname', m.fname)
        user.__setitem__('lname', m.lname)
        user.__setitem__('email', m.email)
        user.__setitem__('disabled', m.disabled)
        user.__setitem__('superuser', m.is_superuser)

        users_list.append(user)
        user = {}

    session = await get_session(request)
    current_user = session['current_user']
    return {'current_user': current_user, 'users': users_list, 'title': 'Users'}


async def user_delete(request):
    """
    Deletes a user from the database through the superuser account.
    :param request:
    :return: '/users' if successful otherwise an exception is raised
    """
    await check_permission(request, 'protected')

    try:
        user_id = request.match_info['id']
        User.delete().where(User.id == user_id).execute()
        raise web.HTTPFound('/users')
    except KeyError:
        return web.Response(status=400)


@aiohttp_jinja2.template('user_mgt/admin_user_edit.html')
async def admin_user_edit(request):
    """
    Retrieves the template for a superuser or administrator to update the details of a user.
    :param request:
    :return: Template with user edit form otherwise an is raised.
    """
    await check_permission(request, 'protected')

    try:
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
        current_user = session['current_user']
        return {'current_user': current_user, 'user': user_selected, 'perm_list': perm_list, 'title': 'User Edit'}
    except KeyError:
        return web.Response(status=400)
    except User.DoesNotExist:
        return web.Response(status=400)


async def admin_user_edit_post(request):
    """
    Updates the details of a user submitted by a superuser or administrator.
    :param request:
    :return: Template showing all users if successful otherwise an exception is raised.
    """
    await check_permission(request, 'protected')
    data = await request.post()

    permissions = []

    try:
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

        if len(permissions) == 0:
            UserPermissions.delete().where(UserPermissions.user_id == user_id).execute()
        else:
            UserPermissions.insert_many(permissions).execute()

        User.update(fname=data['fname'], lname=data['lname'], email=data['email'], is_superuser=superuser,
                    disabled=disabled).where(User.id == user_id).execute()

        raise web.HTTPFound('/users')

    except KeyError:
        return web.Response(status=400)


@aiohttp_jinja2.template('user_mgt/user_profile.html')
async def user_profile(request):
    """
    Retrieves the template showing the profile of a user.
    :param request:
    :return: Template with profile of a user if successful otherwise an exception is raised.
    """
    user_id = await check_authorized(request)

    try:
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
        current_user = session['current_user']
        return {'current_user': current_user, 'user': user_selected, 'title': 'My Account'}
    except User.DoesNotExist:
        web.Response(status=404)


@aiohttp_jinja2.template('user_mgt/change_password.html')
async def change_password(request):
    """
    Retrieves the template for changing the password of a user.
    :param request:
    :return: Template with the change password form otherwise an exception is raised.
    """
    await check_authorized(request)
    session = await get_session(request)
    current_user = session['current_user']
    return {'current_user': current_user, 'title': 'Reset Password'}


async def change_password_post(request):
    """
    Changes the password of a user after the user submits the change password form.
    :param request:
    :return: /'user_profile' template if successful otherwise an exception is raised.
    """
    user_id = await check_authorized(request)
    data = await request.post()
    try:

        if data['password'] == data['confirm_password']:
            try:
                user = User.get(User.id == user_id)
                if check_password_hash(data['old_password'], user.passwd):
                    user.passwd = generate_password_hash(data['password'])
                    user.save()
                    raise web.HTTPFound('/user_profile')
                else:
                    return web.Response(status=404)

            except User.DoesNotExist:
                return web.Response(status=400)
        else:
            # TODO: Return passwords do not match
            return web.Response(status=400)
    except KeyError:
        return web.Response(status=404)
    except User.DoesNotExist:
        return web.Response(text='Invalid data', status=400)


@aiohttp_jinja2.template('user_mgt/user_edit.html')
async def user_edit(request):
    """
    Retrieves the template with the form for editing user details.
    :param request:
    :return: Template with user edit form otherwise an exception is raised.
    """
    user_id = await check_authorized(request)

    try:
        user = User.get(User.id == user_id)
        user_selected = {}

        user_selected.__setitem__('fname', user.fname)
        user_selected.__setitem__('lname', user.lname)
        user_selected.__setitem__('email', user.email)

        session = await get_session(request)
        current_user = session['current_user']
        return {'current_user': current_user, 'user': user_selected, 'title': 'Edit Details'}
    except User.DoesNotExist:
        return web.Response(status=404)


async def user_edit_post(request):
    """
    Updates the details of a user after a user submits the user edit form.
    :param request:
    :return: '/user_profile' template if successful otherwise an exception is raised.
    """
    user_id = await check_authorized(request)
    data = await request.post()

    try:
        user = User.get(User.id == user_id)
        user.fname = data['fname']
        user.lname = data['lname']
        user.email = data['email']
        user.save()

        # Failed to update email with code below.
        # user.update(fname=data['fname'], lname=data['lname'], email=data['email']).execute()

        raise web.HTTPFound('/user_profile')
    except KeyError:
        return web.Response(status=400)
    except User.DoesNotExist:
        return web.Response(status=404)


def setup_user_mgt_routes(app):
    """
    Adds user_mgt routes to the application.
    :param app:
    :return: None
    """
    app.add_routes([
        web.get('/users', users_index, name='users'),
        web.get('/user_profile', user_profile, name='user_profile'),
        web.get('/user_delete/{id}', user_delete, name='user_delete'),
        web.get('/admin_user_edit/{id}', admin_user_edit, name='admin_user_edit'),
        web.post('/admin_user_edit_post', admin_user_edit_post, name='admin_user_edit_post'),
        web.get('/user_edit', user_edit, name='user_edit'),
        web.post('/user_edit_post', user_edit_post, name='user_edit_post'),
        web.get('/change_password', change_password, name='change_password'),
        web.post('/change_password_post', change_password_post, name='change_password_post'),
    ])
