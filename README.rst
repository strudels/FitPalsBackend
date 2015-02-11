
Welcome to Fitpals Web API's documentation!
*******************************************

Contents:

``GET /activities``

   Get all possible activities.

   :Status Codes:
      * 200 OK -- Activities found.

``GET /users``

   Gets users that fall inside the specified parameters.

   :Query Parameters:
      * **longitude** (*float*) -- Specify a longitude to search by.

      * **latitude** (*float*) -- Specify a latitude to search by.

      * **radius** (*int*) -- Specify a radius to search by in meters.

      * **limit** (*int*) -- Limit the number of results.

      * **offset** (*int*) -- Return users after a given offset.

      * **last_updated** (*int*) -- Number of seconds since epoch;
        Return users that were updated before a given time.

      * **jabber_id** (*string*) -- Return users with specific
        jabber_id.

      * **activity_name** (*string*) -- Return users with matching
        activity_name

      * **question_ids** (*int-list*) -- Must be same length as
        answers; specify activity_setting questions to filter by.

      * **answers** (*float-list*) -- Must be same length as
        question_ids; specify answers for activity_settings questions
        to filter by.

   :Status Codes:
      * 200 OK -- Users found.

``POST /users``

   Create new user if not already exists; return user

   :Form Parameters:
      * **str fb_id** -- Specify fb_id for user; must be unique for
        every user.

      * **float longitude** -- Specify a longitude to search by.

      * **float latitude** -- Specify a latitude to search by.

      * **str about_me** -- "About me" description of the user.

      * **str primary_picture** -- Picture ID string for primary
        picture.

      * **int dob** -- Integer number to represent DOB. THIS MAY
        CHANGE!

      * **bool available** -- Specify whether or not user is
        available.

      * **str name** -- Specify user name

      * **str gender** -- Specify user gender; I DON'T THINK THIS
        WORKS

   :Status Codes:
      * 200 OK -- User found.

      * 201 Created -- User created.

      * 400 Bad Request -- Could not create user.

``GET /users/(int: user_id)/activity_settings/(int: activity_id)``

   Get user's activity settings for a specific activity

   :Parameters:
      * **user_id** (*int*) -- Id of user.

      * **activity_id** (*int*) -- Id of acitivity.

   :Query Parameters:
      * **question_id** (*int*) -- Id of question.

   :Status Codes:
      * 400 Bad Request -- User not found.

      * 202 Accepted -- Activity found.

``PUT /users/(int: user_id)/activity_settings/(int: activity_id)``

   Update user's activity settings for a specific activity

   :Request Headers:
      * Authorization -- fb_id token needed here

   :Parameters:
      * **user_id** (*int*) -- Id of user.

      * **activity_id** (*int*) -- Id of acitivity.

   :Form Parameters:
      * **int-list question_ids** -- Ids of questions. Must zip with
        answers

      * **int-list answers** -- Answer to question. Must zip with
        question_ids

   :Status Codes:
      * 400 Bad Request -- "User not found" or "Inequal amounts of
        questions and answers".

      * 202 Accepted -- Activity setting updated.

``DELETE /users/(int: user_id)/activity_settings/(int: activity_id)``

   Delete user's activity settings for a specific activity

   :Request Headers:
      * Authorization -- fb_id token needed here

   :Parameters:
      * **user_id** (*int*) -- Id of user.

      * **activity_id** (*int*) -- Id of acitivity.

   :Form Parameters:
      * **int-list question_ids** -- Ids of questions.

   :Status Codes:
      * 400 Bad Request -- User not found.

      * 202 Accepted -- Activity setting deleted.

``GET /users/(int: owner_id)/messages/(int: other_id)``

   Get owner's messages with other user

   :Parameters:
      * **owner_id** (*int*) -- User id for owner.

      * **other_id** (*int*) -- User id for other user.

   :Status Codes:
      * 400 Bad Request -- User not found.

      * 500 Internal Server Error -- Message lookup failed.

      * 200 OK -- Messages found.

``DELETE /users/(int: owner_id)/messages/(int: other_id)``

   Delete owner's messages with other user

   :Parameters:
      * **owner_id** (*int*) -- User id for owner.

      * **other_id** (*int*) -- User id for other user.

   :Status Codes:
      * 400 Bad Request -- User not found.

      * 500 Internal Server Error -- Messages not deleted.

      * 200 OK -- Messages deleted.

``GET /users/(int: user_id)/activity_settings``

   Get all activity settings for a user

   :Parameters:
      * **user_id** (*int*) -- User to get activity settings for

   :Status Codes:
      * 400 Bad Request -- User not found.

      * 200 OK -- Activity settings found.

``POST /users/(int: user_id)/activity_settings``

   Post new activity setting for user

   :Request Headers:
      * Authorization -- fb_id token needed here

   :Parameters:
      * **user_id** (*int*) -- Id of user.

   :Form Parameters:
      * **int activity_id** -- Id of activity.

      * **int-list question_ids** -- List of question_ids, must zip
        with answers

      * **float-list answers** -- List of answers, must zip with
        question_ids

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 400 Bad Request -- "Inequal numbers of questions and answers"
        or "Activity not found" or "Activity question not found".

      * 202 Accepted -- Activity setting created.

``DELETE /users/(int: user_id)/activity_settings``

   Delete activity settings for user

   :Request Headers:
      * Authorization -- fb_id token needed here

   :Parameters:
      * **user_id** (*int*) -- Id of user.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 400 Bad Request -- User not found.

      * 202 Accepted -- Activity settings created.

``GET /users/(int: user_id)/pictures``

   Get all (secondary)pictures for a user.

   :Parameters:
      * **user_id** (*int*) -- Id of user.

   :Status Codes:
      * 400 Bad Request -- Could not find user.

      * 200 OK -- Pictures found.

``POST /users/(int: user_id)/pictures``

   Post new (secondary)picture for a user.

   :Request Headers:
      * Authorization -- fb_id token needed here

   :Parameters:
      * **user_id** (*int*) -- Id of user.

   :Form Parameters:
      * **str picture_id** -- Facebook Picture Id string.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 400 Bad Request -- Could not find user.

      * 201 Created -- Picture added.

``DELETE /users/(int: user_id)/pictures``

   Delete (secondary)picture for a user.

   :Request Headers:
      * Authorization -- fb_id token needed here

   :Parameters:
      * **user_id** (*int*) -- Id of user.

   :Form Parameters:
      * **str picture_id** -- Facebook Picture Id string.

   :Status Codes:
      * 401 Unauthorized -- Not Authorized.

      * 400 Bad Request -- "Could not find user" or "Picture not
        found".

      * 201 Created -- "Picture removed" or "Pictures removed".

``GET /users/(int: user_id)/matches``

   :Parameters:
      * **user_id** (*int*) -- User id for owner of matches.

   :Query Parameters:
      * **liked** (*bool*) -- If specified, returns matches that
        correspond with liked.

   :Status Codes:
      * 400 Bad Request -- User not found.

      * 200 OK -- Matches retrieved.

``POST /users/(int: user_id)/matches``

   :Request Headers:
      * Authorization -- fb_id token needed here

   :Parameters:
      * **user_id** (*int*) -- User id for owner of matches.

   :Form Parameters:
      * **int match_id** -- User id for match.

      * **bool liked** -- If specified, returns matches that
        correspond with liked.

   :Status Codes:
      * 400 Bad Request -- "User not found" or "Match not found".

      * 200 OK -- Match posted.

``DELETE /users/(int: user_id)/matches``

   :Request Headers:
      * Authorization -- fb_id token needed here

   :Parameters:
      * **user_id** (*int*) -- User id for owner of matches.

   :Form Parameters:
      * **int match_id** -- User id for match.

   :Status Codes:
      * 400 Bad Request -- User not found.

      * 200 OK -- User match decisions deleted.

``POST /users/(user_id)/apn_tokens``

   Post new APN token for user

   :Request Headers:
      * Authorization -- fb_id token needed here

   :Parameters:
      * **user_id** (*int*) -- Id of user.

   :Form Parameters:
      * **str token** -- apn_token to be posted

   :Status Codes:
      * 400 Bad Request -- Could not find user.

      * 201 Created -- APN token stored.

``DELETE /users/(user_id)/apn_tokens``

   Delete APN token for user

   :Request Headers:
      * Authorization -- fb_id token needed here

   :Parameters:
      * **user_id** (*int*) -- Id of user.

   :Form Parameters:
      * **str token** -- apn_token to be deleted. If not specified,
        all apn_tokens will be deleted.

   :Status Codes:
      * 400 Bad Request -- Could not find user.

      * 201 Created -- APN token stored.

``GET /users/(int: user_id)``

   Get a user object by user_id

   :Request Headers:
      * Authorization -- fb_id token needed for private values;
        currently does nothing

   :Parameters:
      * **user_id** (*int*) -- User to delete.

   :Query Parameters:
      * **attributes** (*str-list*) -- list of user attribute names to
        receive; if left empty, all attributes will be returned

   :Status Codes:
      * 200 OK -- User found.

      * 400 Bad Request -- User not found.

``PUT /users/(int: user_id)``

   Update a user

   :Request Headers:
      * Authorization -- fb_id token needed here

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
      * 400 Bad Request -- "Could not find user" or "User updated
        failed".

      * 401 Unauthorized -- Not Authorized.

      * 202 Accepted -- User updated.

``DELETE /users/(int: user_id)``

   Delete a user

   :Request Headers:
      * Authorization -- fb_id token needed here

   :Parameters:
      * **user_id** (*int*) -- User to delete.

   :Status Codes:
      * 400 Bad Request -- Could not find user.

      * 401 Unauthorized -- Not Authorized.

      * 500 Internal Server Error -- User not deleted.

      * 202 Accepted -- User updated.


Indices and tables
******************

* `Index <wiki/Genindex>`_

* `Module Index <wiki/Py-Modindex>`_

* `Search Page <wiki/Search>`_
