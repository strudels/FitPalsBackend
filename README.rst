
Welcome to Fitpals Web API's documentation!
*******************************************

Contents:

``GET /admin/userreport/ajax/lookup/``

``POST /admin/userreport/ajax/update/``

   Edits a single column of a record in list view.

``GET /admin/activity/ajax/lookup/``

``POST /admin/activity/ajax/update/``

   Edits a single column of a record in list view.

``GET /admin/question/ajax/lookup/``

``POST /admin/question/ajax/update/``

   Edits a single column of a record in list view.

``POST /admin/userreport/action/``

   Mass-model action view.

``POST /admin/userreport/delete/``

   Delete model view. Only POST method is allowed.

``GET /admin/userreport/edit/``

   Edit model view

``POST /admin/userreport/edit/``

   Edit model view

``GET /admin/userreport/new/``

   Create model view

``POST /admin/userreport/new/``

   Create model view

``POST /admin/activity/action/``

   Mass-model action view.

``POST /admin/activity/delete/``

   Delete model view. Only POST method is allowed.

``POST /admin/question/action/``

   Mass-model action view.

``POST /admin/question/delete/``

   Delete model view. Only POST method is allowed.

``GET /admin/activity/edit/``

   Edit model view

``POST /admin/activity/edit/``

   Edit model view

``GET /admin/question/edit/``

   Edit model view

``POST /admin/question/edit/``

   Edit model view

``GET /admin/activity/new/``

   Create model view

``POST /admin/activity/new/``

   Create model view

``GET /admin/question/new/``

   Create model view

``POST /admin/question/new/``

   Create model view

``GET /admin/userreport/``

   List view

``GET /admin/activity/``

   List view

``GET /admin/question/``

   List view

``GET /admin/logout``

``GET /admin/login``

``POST /admin/login``

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
      * 400 Bad Request -- Activity setting data invalid.

      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Question not found.

      * 404 Not Found -- User not found.

      * 201 Created -- Activity setting created.

``GET /facebook_friends``

   Gets a user's(specified by Authorization) facebook friends(As User
   objects).

   :Request Headers:
      * Authorization -- fitpals secret

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 200 OK -- Friends found.

``GET /message_threads``

   Get all message threads for a user, specified by Authorization

   Will not return any message threads that have been "deleted".

   :Request Headers:
      * Authorization -- facebook secret

   :Query Parameters:
      * **other_user_id** (*int*) -- Get message thread between
        requester and other_user

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 200 OK -- Message threads found.

``POST /message_threads``

   Create new message thread between 2 users.

   If a message thread already exists between 2 users, that message
   thread is returned. Even if that message thread was previously
   deleted by the POSTing user.

   :Request Headers:
      * Authorization -- fitpals_secret

   :Form Parameters:
      * **int user2_id** -- Id of user2 for new message thread.

   :Status Codes:
      * 400 Bad Request -- Message thread data invalid.

      * 401 Unauthorized -- Not Authorized.

      * 403 Forbidden -- Blocked from creating message thread.

      * 404 Not Found -- user2_id not found.

      * 201 Created -- Message thread created.

``GET /search_settings``

   Get search settings.

   :Request Headers:
      * Authorization -- facebook secret

   :Parameters:
      * **user_id** (*int*) -- Id of user that owns the search
        settings.

   :Status Codes:
      * 404 Not Found -- User not found.

      * 200 OK -- Search settings found.

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

      * 404 Not Found -- User not found.

      * 201 Created -- User report created.

``GET /user_blocks``

   Get a user's UserBlocks.

   :Request Headers:
      * Authorization -- fitpals_secret

   :Query Parameters:
      * **blocked_user_id** (*int*) -- Id of blocked_user

   :Status Codes:
      * 404 Not Found -- User not found

      * 401 Unauthorized -- Not Authorized.

      * 200 OK -- User blocks found.

``POST /user_blocks``

   Post a new UserBlock.

   :Request Headers:
      * Authorization -- fitpals_secret

   :Form Parameters:
      * **int blocked_user_id** -- ID of user to be blocked.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 403 Forbidden -- User already blocked.

      * 404 Not Found -- User not found.

      * 201 Created -- User block created.

``GET /activities``

   Get all possible activities.

   :Status Codes:
      * 200 OK -- Activities found.

``GET /questions``

   Get all questions for all activities.

   :Status Codes:
      * 200 OK -- Questions found.

``GET /messages``

   Get owner's messages from a thread

   Does not return messages from threads that have been "deleted."

   :Request Headers:
      * Authorization -- facebook secret

   :Query Parameters:
      * **message_thread_id** (*int*) -- Id of specific thread to get
        messages from(Optional).

      * **since** (*int*) -- Optional time to get messages 'since'
        then(epoch).

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Message thread not found.

      * 200 OK -- Messages found.

``POST /messages``

   Post new message to thread The receiving user of the message's
   corresponding MessageThread.user<1/2>_has_unread field will be set
   to True

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
      * 400 Bad Request -- Message data invalid.

      * 401 Unauthorized -- Not Authorized.

      * 403 Forbidden -- Message thread has been closed.

      * 404 Not Found -- Message thread not found.

      * 201 Created -- Message created.

``GET /pictures``

   Get all pictures for a user.

   :Query Parameters:
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

      * **float top** -- Top position for crop. Must be between 0 and
        1.

      * **float bottom** -- Bottom position for crop. Must be between
        0 and 1.

      * **float left** -- Left position for crop. Must be between 0
        and 1.

      * **float right** -- Right position for crop. Must be between 0
        and 1.

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
      * 400 Bad Request -- Device data invalid.

      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- User not found.

      * 200 OK -- Device already registered.

      * 201 Created -- Device registered.

``GET /matches``

   Get matches for a user

   :Request Headers:
      * Authorization -- facebook secret

   :Query Parameters:
      * **mutual** (*int*) -- If specified, returns matches where
        other user has also matched with the querying user. Set to 0
        for False, 1 for True.

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
      * 400 Bad Request -- Match data invalid.

      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- User not found.

      * 404 Not Found -- Match user not found.

      * 201 Created -- Match created.

``GET /friends``

   Get friends(as User objects) for a user specified by Authorization.

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
      * **int id** -- Id of user to be added to friends list.

   :Status Codes:
      * 400 Bad Request -- Friend data invalid.

      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- User not found.

      * 201 Created -- Friend added.

``GET /users``

   Gets users that fall inside the specified parameters
      and the authorized user's search settings

   :Request Headers:
      * Authorization -- facebook secret

   :Query Parameters:
      * **limit** (*int*) -- Limit the number of results.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 500 Internal Server Error -- Internal Error.

      * 200 OK -- Users found.

``POST /users``

   Create new user if not already exists; return user

   :Form Parameters:
      * **str access_token** -- Specify fb access token for user from
        login dialogue.

      * **float longitude** -- Specify a longitude to search by.

      * **float latitude** -- Specify a latitude to search by.

      * **str about_me** -- "About me" description of the user.

      * **int dob_year** -- Integer number to represent DOB year.

      * **int dob_month** -- Integer number to represent DOB month.

      * **int dob_day** -- Integer number to represent DOB day.

      * **str name** -- Specify user name

      * **str gender** -- Specify user gender; I DON'T THINK THIS
        WORKS

   :Status Codes:
      * 400 Bad Request -- Invalid user data.

      * 401 Unauthorized -- Not Authorized.

      * 200 OK -- User found.

      * 201 Created -- User created.

``GET /admin/``

``GET /activities/(int: activity_id)/questions``

   Get all questions for an activity.

   :Status Codes:
      * 404 Not Found -- Activity not found.

      * 200 OK -- Questions found.

``GET /admin/static/(path: filename)``

   Function used internally to send static files from the static
   folder to the browser.

   New in version 0.5: New in version 0.5.

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
      * 400 Bad Request -- Activity settings data invalid.

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

``GET /message_threads/(int: thread_id)``

   Get a message_thread by it's ID.

   :Request Headers:
      * Authorization -- fitpals_secret

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Message thread not found.

      * 200 OK -- Message thread found.

``PUT /message_threads/(int: thread_id)``

   Update a message_thread's user<1/2>_has_unread field to False.

   :Request Headers:
      * Authorization -- fitpals_secret

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Message thread not found.

      * 202 Accepted -- Message thread updated.

``DELETE /message_threads/(int: thread_id)``

   Delete a message thread

   NOTE: does not actually delete the message thread. Instead, calling
   this route causes all messages within the thread to appear to have
   been deleted. In reality, these messages are still available to the
   other user(assuming they have not deleted the thread). After
   deleting a thread, the thread will no longer show up in GET
   /message_threads until a new message is POST'd to it. Messages
   before a delete will become unavailable from GET /messages after
   the delete, but messages after the delete will be available.

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

   NOTE bool fields friends_only, men, and women are encoded as int
   because reqparse is dumb and I should've used something else.

   :Request Headers:
      * Authorization -- facebook secret

   :Parameters:
      * **settings_id** (*int*) -- Id of search settings.

   :Form Parameters:
      * **int available** -- Set to 1 if user wants to be available;
        Default is 0.

      * **int friends_only** -- Set to 1 if user wants friends only;
        Default is 0.

      * **int men** -- Set to 0 if user don't wants men; Default is 1.

      * **int women** -- Set to 1 if user don't wants women; Default
        is 1.

      * **int age_lower_limit** -- Set if user want lower age limit.
        Default is 18.

      * **int age_upper_limit** -- Set if user want upper age limit.
        Default is 130.

   http://en.wikipedia.org/wiki/Oldest_people

   :Status Codes:
      * 400 Bad Request -- Search settings data invalid.

      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Search settings not found.

      * 202 Accepted -- Search settings updated.

``DELETE /user_blocks/(int: block_id)``

   Remove a UserBlock.

   :Request Headers:
      * Authorization -- fitpals_secret

   :Parameters:
      * **block_id** (*int*) -- ID of UserBlock.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- User block not found.

      * 200 OK -- User block removed.

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
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Device not found.

      * 200 OK -- Device deleted.

``PUT /matches/(int: match_id)``

   Update match read field to true.

   :Request Headers:
      * Authorization -- fitpals_secret

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Match not found.

      * 202 Accepted -- Match updated.

``DELETE /matches/(int: match_id)``

   Delete match

   :Request Headers:
      * Authorization -- facebook secret

   :Parameters:
      * **match_id** (*int*) -- Id for specific match.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 404 Not Found -- Match not found.

      * 200 OK -- Match deleted.

``DELETE /friends/(int: friend_id)``

   Delete a friend.

   :Request Headers:
      * Authorization -- facebook secret

   :Parameters:
      * **friend_id** (*int*) -- User Id of friend to delete.

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

      * **str about_me** -- Update user's about_me

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
