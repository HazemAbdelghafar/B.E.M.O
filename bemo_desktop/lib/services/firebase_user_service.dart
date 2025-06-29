import 'dart:convert';
import 'package:http/http.dart' as http;
import 'websocket_service.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
// import 'package:google_sign_in/google_sign_in.dart';

class FirebaseUserService {
  final String _projectId =
      dotenv.env['projectId'] ?? ''; // Your Firebase project ID
  final String _apiKey = dotenv.env['apiKey'] ?? '';
  // final String _clientId = dotenv.env['clientId'] ?? '';
  // final GoogleSignIn _googleSignIn = GoogleSignIn.instance;

  Future<Map<String, dynamic>> signUp(String email, String password) async {
    final url = Uri.parse(
      'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=$_apiKey',
    );

    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
        'returnSecureToken': true,
      }),
    );

    return jsonDecode(response.body);
  }

  Future<Map<String, dynamic>> signIn(String email, String password) async {
    final url = Uri.parse(
      'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=$_apiKey',
    );

    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
        'returnSecureToken': true,
      }),
    );

    return jsonDecode(response.body);
  }

  //   Future<Map<String, dynamic>> signInWithGoogle() async {
  //   try {
  //     final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
  //     if (googleUser == null) {
  //       // User canceled the sign-in
  //       return {'error': 'Sign in aborted by user'};
  //     }

  //     final GoogleSignInAuthentication googleAuth =
  //         await googleUser.authentication;

  //     final String? idToken = googleAuth.idToken;
  //     final String? accessToken = googleAuth.accessToken;

  //     if (idToken == null) {
  //       return {'error': 'Failed to get Google ID token'};
  //     }

  //     // Now exchange with Firebase REST API
  //     final response = await http.post(
  //       Uri.parse(
  //         'https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key=$apiKey',
  //       ),
  //       body: jsonEncode({
  //         'postBody': 'id_token=$idToken&providerId=google.com',
  //         'requestUri': 'http://localhost',
  //         'returnIdpCredential': true,
  //         'returnSecureToken': true,
  //       }),
  //       headers: {'Content-Type': 'application/json'},
  //     );

  //     final data = jsonDecode(response.body);

  //     if (response.statusCode == 200) {
  //       return {
  //         'uid': data['localId'],
  //         'idToken': data['idToken'],
  //         'email': data['email'],
  //       };
  //     } else {
  //       print('Firebase Google sign-in error: $data');
  //       return {'error': data['error']['message'] ?? 'Unknown error'};
  //     }
  //   } catch (e) {
  //     print('Google sign-in failed: $e');
  //     return {'error': e.toString()};
  //   }
  // }

  // Future<Map<String, dynamic>> signUpWithGoogle() async {
  //   final Uri googleOAuthUrl = Uri.parse(
  //     'https://accounts.google.com/o/oauth2/v2/auth'
  //     '?client_id=$clientId'
  //     '&redirect_uri=http://localhost' // can be custom URI scheme for mobile
  //     '&response_type=token'
  //     '&scope=email profile openid',
  //   );
  //   if (await canLaunchUrl(googleOAuthUrl)) {
  //     await launchUrl(googleOAuthUrl);
  //     print('opened');
  //   } else {
  //     throw Exception('Could not launch $googleOAuthUrl');
  //   }
  //   print(googleOAuthUrl.queryParameters);
  //   final idToken = googleOAuthUrl.queryParameters['id_token']!;
  //   print('idToken: $idToken');

  //   final response = await http.post(
  //     Uri.parse(
  //       'https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key=YOUR_FIREBASE_API_KEY',
  //     ),
  //     headers: {'Content-Type': 'application/json'},
  //     body: json.encode({
  //       'postBody': 'id_token=$idToken&providerId=google.com',
  //       'requestUri': 'http://localhost',
  //       'returnIdpCredential': true,
  //       'returnSecureToken': true,
  //     }),
  //   );
  //   return jsonDecode(response.body);
  // }

  Future<Map<String, dynamic>> changePassword(
    String idToken,
    String newPassword,
  ) async {
    final url =
        'https://identitytoolkit.googleapis.com/v1/accounts:update?key=$_apiKey';

    final response = await http.post(
      Uri.parse(url),
      body: jsonEncode({
        "idToken": idToken,
        "password": newPassword,
        "returnSecureToken": true,
      }),
      headers: {'Content-Type': 'application/json'},
    );

    return jsonDecode(response.body);
  }

  Future<Map<String, dynamic>> sendPasswordResetEmail(String email) async {
    final url =
        'https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key=$_apiKey';

    final response = await http.post(
      Uri.parse(url),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'requestType': 'PASSWORD_RESET', 'email': email}),
    );

    return jsonDecode(response.body);
  }

  Future<String?> getUserEmail(String idToken) async {
    final url =
        'https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=$_apiKey';

    final response = await http.post(
      Uri.parse(url),
      body: jsonEncode({'idToken': idToken}),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);

      final users = data['users'] as List<dynamic>;
      if (users.isNotEmpty) {
        final user = users[0];
        return user['email'] as String?;
      } else {
        return null; // No user found
      }
    } else {
      throw Exception(
        'Failed to fetch user info: ${response.statusCode} ${response.body}',
      );
    }
  }

  Future<void> saveUserData({
    required String uid,
    required String idToken,
    required Map<String, dynamic> data,
  }) async {
    final url = Uri.parse(
      'https://firestore.googleapis.com/v1/projects/$_projectId/databases/(default)/documents/users?documentId=$uid',
    );

    // Convert to Firestore JSON format
    Map<String, dynamic> firestoreFormatted = {
      "fields": data.map((key, value) => MapEntry(key, {"stringValue": value})),
    };

    final response = await http.post(
      url,
      headers: {
        'Authorization': 'Bearer $idToken',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(firestoreFormatted),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      print("User data saved successfully!");
    } else {
      print("Failed to save user data: ${response.body}");
      throw Exception('Failed to save user data');
    }

    print("Saved data from getting started page: $data");

    // // Todo: Remove this and implement websocket service function to send user data to websocket
    try {
      WebSocketService().send({
        'src_user_id': 'user-MK1',
        'data': data,
      }); //Todo: Change this to the user's robot id (user-MK1)
    } catch (e) {
      print("Failed to send user data to websocket: $e");
    }
  }

  // // Todo: Implement function to fetch user data from firebase
  Future<Map<String, dynamic>> fetchUserData({
    required String uid,
    required String idToken,
  }) async {
    final url = Uri.parse(
      'https://firestore.googleapis.com/v1/projects/$_projectId/databases/(default)/documents/users/$uid',
    );

    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $idToken',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      // Extract the fields from Firestore format
      if (data['fields'] != null) {
        Map<String, dynamic> userData = {};
        data['fields'].forEach((key, value) {
          if (value is Map && value.containsKey('stringValue')) {
            userData[key] = value['stringValue'];
          }
        });
        return userData;
      }
      return data;
    } else {
      print(
        "Failed to fetch user data: ${response.statusCode} - ${response.body}",
      );
      throw Exception('Failed to fetch user data');
    }
  }

  // // Todo: Implement function to update user data in firebase
  Future<void> updateUserData({
    required String uid,
    required String idToken,
    required Map<String, dynamic> data,
  }) async {
    final url = Uri.parse(
      'https://firestore.googleapis.com/v1/projects/$_projectId/databases/(default)/documents/users/$uid',
    );

    // Convert to Firestore JSON format
    Map<String, dynamic> firestoreFormatted = {
      "fields": data.map((key, value) => MapEntry(key, {"stringValue": value})),
    };

    final response = await http.patch(
      url,
      headers: {
        'Authorization': 'Bearer $idToken',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(firestoreFormatted),
    );

    if (response.statusCode == 200) {
      print("User data updated successfully!");
    } else {
      print(
        "Failed to update user data: ${response.statusCode} - ${response.body}",
      );
      throw Exception('Failed to update user data');
    }
  }

  // // Todo: Implement function to delete user data from firebase
  Future<void> deleteUserData({
    required String uid,
    required String idToken,
  }) async {
    final url = Uri.parse(
      'https://firestore.googleapis.com/v1/projects/$_projectId/databases/(default)/documents/users/$uid',
    );

    final response = await http.delete(
      url,
      headers: {
        'Authorization': 'Bearer $idToken',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      print("User data deleted successfully!");
    } else {
      print(
        "Failed to delete user data: ${response.statusCode} - ${response.body}",
      );
      throw Exception('Failed to delete user data');
    }
  }

  Future<void> deleteUser(String idToken) async {
    final url = Uri.parse(
      'https://identitytoolkit.googleapis.com/v1/accounts:delete?key=$_apiKey',
    );
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'idToken': idToken}),
    );
    if (response.statusCode == 200) {
      print("User deleted successfully!");
    } else {
      print("Failed to delete user: ${response.statusCode} - ${response.body}");
      throw Exception('Failed to delete user');
    }
  }
}
