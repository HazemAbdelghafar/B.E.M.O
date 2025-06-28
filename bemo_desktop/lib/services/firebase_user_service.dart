import 'dart:convert';
import 'package:http/http.dart' as http;
import 'websocket_service.dart';

class FirebaseUserService {
  final String projectId = 'b-e-m-o'; // Your Firebase project ID

  Future<void> saveUserData({
    required String uid,
    required String idToken,
    required Map<String, dynamic> data,
  }) async {
    final url = Uri.parse(
      'https://firestore.googleapis.com/v1/projects/$projectId/databases/(default)/documents/users?documentId=$uid',
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

    print(data);

    //Todo: Remove this and implement websocket service function to send user data to websocket
    try {
      WebSocketService().connect();
      WebSocketService().send({'src_user_id': 'user-MK2', 'data': data});
    } catch (e) {
      print("Failed to send user data to websocket: $e");
    }
  }

  //Todo: Implement function to fetch user data from firebase
}
