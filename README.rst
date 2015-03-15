
Welcome to Fitpals Web API's documentation!
*******************************************

Contents:

``GET /activity_settings``

   Get all activity settings for a user, specified by Authorization

   :Request Headers:
      * Authorization -- facebook secret

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 200 OK -- Activity settings found.

``POST /activity_settings``

   Post new activity setting for user

   :Request Headers:
      * Authorization -- facebook secret

   :Form Parameters:
      * **int user_id** -- Id of user.

      * **int question_id** -- Id of question.

      * **float lower_value** -- Lower value answer for question.

      * **float upper_value** -- Upper value answer for question.

      * **str unit_type** -- Name of type of unit; i.e. meter

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Question not found.

      * 404 Not Found -- User not found.

      * 500 Internal Server Error -- Could not create activity
        setting.

      * 201 Created -- Activity setting created.

``GET /message_threads``

   Get all message threads for a user, specified by Authorization

   :Request Headers:
      * Authorization -- facebook secret

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 200 OK -- Message threads found.

``POST /message_threads``

   Create new message thread between 2 users.

   :Request Headers:
      * Authorization -- facebook secret

   :Form Parameters:
      * **int user2_id** -- Id of user2 for new message thread.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- user2_id not found.

      * 500 Internal Server Error -- Internal Error. Changes not
        committed.

      * 201 Created -- Message thread created.

``POST /user_reports``

   Report User by creating new UserReport.

   :Request Headers:
      * Authorization -- facebook secret

   :Form Parameters:
      * **str owner_fb_id** -- Facebook id of person sending report

      * **str reported_fb_id** -- Facebook id of person being reported

      * **str reason** -- Reason for why person is being reported

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- fb_id not found.

      * 500 Internal Server Error -- Internal error. Changes not
        committed.

      * 201 Created -- User report created.

``GET /activities``

   Get all possible activities.

   :Status Codes:
      * 200 OK -- Activities found.

``GET /messages``

   Get owner's messages from a thread

   :Request Headers:
      * Authorization -- facebook secret

   :Query Parameters:
      * **message_thread_id** (*int*) -- Id of specific thread to get
        messages from.

      * **since** (*int*) -- Optional time to get messages 'since'
        then.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Message thread not found.

      * 200 OK -- Messages found.

``POST /messages``

   Post new message to thread

   :Request Headers:
      * Authorization -- facebook secret

   :Form Parameters:
      * **int message_thread_id** -- Id of specific thread to get
        messages from.

      * **str body** -- Message body

      * **int direction** -- direction that message goes between users
        1 and  2 in a thread. Set to 0 for user1->user2; Set to 1 for
        user2->user1. Note: direction's type  in the model is actually
        boolean, where 0->False and 1->True.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 403 Forbidden -- Message thread has been closed.

      * 404 Not Found -- Message thread not found.

      * 500 Internal Server Error -- Internal Error. Changes not
        committed.

      * 201 Created -- Message created.

``GET /pictures``

   Get all pictures for a user.

   :Parameters:
      * **user_id** (*int*) -- Id of user.

   :Status Codes:
      * 404 Not Found -- User not found.

      * 200 OK -- Pictures found.

``POST /pictures``

   Post new picture.

   :Request Headers:
      * Authorization -- facebook secret

   :Form Parameters:
      * **int user_id** -- Id of user.

      * **str uri** -- Facebook Picture Id string.

      * **int ui_index** -- Index of the ui.

      * **float top** -- Top position for crop

      * **float bottom** -- Bottom position for crop

      * **float left** -- Left position for crop

      * **float right** -- Right position for crop

   :Status Codes:
      * 400 Bad Request -- Picture data invalid.

      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- User not found.

      * 201 Created -- Picture added.

``POST /devices``

   Post new device

   :Request Headers:
      * Authorization -- facebook secret

   :Form Parameters:
      * **int user_id** -- Id of user.

      * **str token** -- device token to be posted

   :Status Codes:
      * 400 Bad Request -- Could not register device.

      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- User not found.

      * 200 OK -- Device already registered.

      * 201 Created -- Device registered.

``GET /matches``

   Get matches for a user

   :Request Headers:
      * Authorization -- facebook secret

   :Query Parameters:
      * **liked** (*bool*) -- If specified, returns matches that
        correspond with liked. Set to 0 for False, 1 for True.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 200 OK -- Matches found.

``POST /matches``

   Create new match

   :Request Headers:
      * Authorization -- facebook secret

   :Form Parameters:
      * **int user_id** -- User id for owner of matches.

      * **int matched_user_id** -- User id for matched user.

      * **bool liked** -- If specified, sets new match liked. Set to 0
        for False, 1 for True.

   :Status Codes:
      * 400 Bad Request -- Could not create match.

      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- User not found.

      * 404 Not Found -- Match user not found.

      * 201 Created -- Match created.

``GET /friends``

   Get friends for a user specified by Authorization.

   :Request Headers:
      * Authorization -- facebook secret

   :Status Codes:
      * 200 OK -- Friends found.

      * 401 Unauthorized -- Not Authorized.

``POST /friends``

   Add friend to friends list.

   :Request Headers:
      * Authorization -- facebook secret

   :Form Parameters:
      * **int user_id** -- Id of user creating friend.

      * **int friend_user_id** -- Id of user to be friend.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- User not found.

      * 500 Internal Server Error -- Internal error. Changes not
        committed.

      * 201 Created -- Friends added.

``GET /users``

   Gets users that fall inside the specified parameters
      and the authorized user's search settings

   :Request Headers:
      * Authorization -- facebook secret

   :Query Parameters:
      * **longitude** (*float*) -- Specify a longitude to search by.

      * **latitude** (*float*) -- Specify a latitude to search by.

      * **radius** (*int*) -- Specify a radius to search by in meters.

      * **limit** (*int*) -- Limit the number of results.

      * **offset** (*int*) -- Return users after a given offset.

      * **last_updated** (*int*) -- Number of seconds since epoch;
        Return users that were updated before a given time.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 500 Internal Server Error -- Internal Error.

      * 200 OK -- Users found.

``POST /users``

   Create new user if not already exists; return user

   :Form Parameters:
      * **str fb_id** -- Specify fb_id for user; must be unique for
        every user.

      * **str fb_secret** -- Specify fb_secret for user; must be
        unique for every user.

      * **float longitude** -- Specify a longitude to search by.

      * **float latitude** -- Specify a latitude to search by.

      * **str about_me** -- "About me" description of the user.

      * **str primary_picture** -- Picture ID string for primary
        picture.

      * **int dob_year** -- Integer number to represent DOB year.

      * **int dob_month** -- Integer number to represent DOB month.

      * **int dob_day** -- Integer number to represent DOB day.

      * **bool available** -- Specify whether or not user is
        available.

      * **str name** -- Specify user name

      * **str gender** -- Specify user gender; I DON'T THINK THIS
        WORKS

   :Status Codes:
      * 400 Bad Request -- Must specify DOB.

      * 400 Bad Request -- Could not create user.

      * 401 Unauthorized -- Not Authorized.

      * 500 Internal Server Error -- Internal error. Changes not
        committed.

      * 200 OK -- User found.

      * 201 Created -- User created.

``GET /activity_settings/(int: setting_id)``

   Get specific activity setting

   :Request Headers:
      * Authorization -- facebook secret

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Activity setting not found.

      * 202 Accepted -- Activity setting found.

``PUT /activity_settings/(int: setting_id)``

   Update specific activity setting

   :Request Headers:
      * Authorization -- facebook secret

   :Form Parameters:
      * **float lower_value** -- Lower value answer to question.

      * **float upper_value** -- Upper value answer to question.

      * **str unit_type** -- Name of type of unit; i.e. meter

   :Status Codes:
      * 400 Bad Request -- Could not update activity setting.

      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Activity setting not found.

      * 202 Accepted -- Activity setting updated.

``DELETE /activity_settings/(int: setting_id)``

   Delete Activity Setting

   :Request Headers:
      * Authorization -- facebook secret

   :Parameters:
      * **setting_id** (*int*) -- Id of activity setting.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Activity setting not found.

      * 500 Internal Server Error -- Internal error. Changes not
        committed.

      * 202 Accepted -- Activity setting deleted.

``DELETE /message_threads/(int: thread_id)``

   Delete a message thread

   :Request Headers:
      * Authorization -- facebook secret

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Message thread not found.

      * 500 Internal Server Error -- Internal Error. Changes not
        committed.

      * 200 OK -- Message thread deleted.

``GET /search_settings/(int: settings_id)``

   Get search settings.

   :Request Headers:
      * Authorization -- facebook secret

   :Parameters:
      * **settings_id** (*int*) -- Id of search settings.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Search settings not found.

      * 200 OK -- Search settings found.

``PUT /search_settings/(int: settings_id)``

   Create new search setting.

   NOTE bool fields friends_only, men_only, and women_only are encoded
   as int because reqparse is dumb and I should've used something
   else.

   :Request Headers:
      * Authorization -- facebook secret

   :Parameters:
      * **settings_id** (*int*) -- Id of search settings.

   :Form Parameters:
      * **int activity_id** -- Activity id.

      * **int friends_only** -- Set to 1 if user wants friends only;
        Default is 0

      * **int men_only** -- Set to 1 if user wants men only; Default
        is 0

      * **int women_only** -- Set to 1 if user wants women only;
        Default is 0

      * **int age_lower_limit** -- Set if user want lower age limit.
        Default is 18.

      * **int age_upper_limit** -- Set if user want upper age limit.
        Default is 130.

   http://en.wikipedia.org/wiki/Oldest_people

   :Status Codes:
      * 400 Bad Request -- Search settings could not be updated.

      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Search settings not found.

      * 202 Accepted -- Search settings updated.

``PUT /pictures/(int: pic_id)``

   Delete picture.

   :Request Headers:
      * Authorization -- facebook secret

   :Parameters:
      * **pic_id** (*int*) -- Id of user.

   :Form Parameters:
      * **int user_id** -- Id of user.

      * **str uri** -- Facebook Picture Id string.

      * **int ui_index** -- Index of the ui.

      * **float top** -- Top position for crop

      * **float bottom** -- Bottom position for crop

      * **float left** -- Left position for crop

      * **float right** -- Right position for crop

   :Status Codes:
      * 400 Bad Request -- Picture data invalid.

      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Picture not found.

      * 201 Created -- Picture removed.

``DELETE /pictures/(int: pic_id)``

   Delete picture.

   :Request Headers:
      * Authorization -- facebook secret

   :Parameters:
      * **pic_id** (*int*) -- Id of user.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Picture not found.

      * 500 Internal Server Error -- Internal error. Changes not
        committed.

      * 201 Created -- Picture removed.

``DELETE /devices/(int: device_id)``

   Delete device

   :Request Headers:
      * Authorization -- facebook secret

   :Status Codes:
      * 400 Bad Request -- Could not delete device.

      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Device not found.

      * 200 OK -- Device deleted.

``DELETE /matches/(int: match_id)``

   Delete match

   :Request Headers:
      * Authorization -- facebook secret

   :Parameters:
      * **match_id** (*int*) -- Id for specific match.

   :Status Codes:
      * 400 Bad Request -- Match could not be deleted.

      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Match not found.

      * 200 OK -- Match deleted.

``DELETE /friends/(int: friend_id)``

   Delete a friend.

   :Request Headers:
      * Authorization -- facebook secret

   :Parameters:
      * **friend_id** (*int*) -- Id of friend to delete.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Friend not found.

      * 500 Internal Server Error -- Internal error. Changes not
        committed.

      * 200 OK -- Friend deleted.

``GET /users/(int: user_id)``

   Get a user object by user_id

   :Parameters:
      * **user_id** (*int*) -- User to delete.

   :Query Parameters:
      * **attributes** (*str-list*) -- list of user attribute names to
        receive; if left empty, all attributes will be returned

   :Status Codes:
      * 200 OK -- User found.

      * 404 Not Found -- User not found.

``PUT /users/(int: user_id)``

   Update a user

   :Request Headers:
      * Authorization -- facebook secret

   :Parameters:
      * **user_id** (*int*) -- User to delete.

   :Form Parameters:
      * **float longitude** -- Update user's longitude. Latitude must
        also be specified.

      * **float latitude** -- Update user's latitude. Longitude must
        also be specified.

      * **str primary_picture** -- Update user's primary_picture

      * **str about_me** -- Update user's about_me

      * **bool available** -- Update user's availability

      * **int dob** -- Update user's DOB; THIS WILL LIKELY CHANGE

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- User not found.

      * 500 Internal Server Error -- Internal error. Changes not
        committed.

      * 202 Accepted -- User updated.

``DELETE /users/(int: user_id)``

   Delete a user

   :Request Headers:
      * Authorization -- facebook secret

   :Parameters:
      * **user_id** (*int*) -- User to delete.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- User not found.

      * 500 Internal Server Error -- User not deleted.

      * 202 Accepted -- User updated.


Indices and tables
******************

* `Index <wiki/Genindex>`_

* `Module Index <wiki/Py-Modindex>`_

* `Search Page <wiki/Search>`_
