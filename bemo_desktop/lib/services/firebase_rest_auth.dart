import 'dart:convert';
import 'package:http/http.dart' as http;

class FirebaseRestAuth {
  final String apiKey = 'AIzaSyAd7AHSiRCLNZkIKCV2AgnkIRNrMcl9yBs';

  Future<Map<String, dynamic>> signUp(String email, String password) async {
    final url = Uri.parse(
      'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=$apiKey',
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
      'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=$apiKey',
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

  Future<Map<String, dynamic>> changePassword(
    String idToken,
    String newPassword,
  ) async {
    final url =
        'https://identitytoolkit.googleapis.com/v1/accounts:update?key=$apiKey';

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
        'https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key=$apiKey';

    final response = await http.post(
      Uri.parse(url),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'requestType': 'PASSWORD_RESET', 'email': email}),
    );

    return jsonDecode(response.body);
  }
}
