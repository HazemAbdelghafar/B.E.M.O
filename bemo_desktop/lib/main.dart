import 'package:flutter/material.dart';
import 'app.dart';
import 'services/websocket_service.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: "assets/.env");
  WebSocketService().connect();
  runApp(BemoApp());
}
