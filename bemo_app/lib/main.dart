import 'package:flutter/material.dart';
import 'services/websocket_service.dart';
import 'dashboard.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  // Establish WebSocket connection when app starts - will stay connected across all pages
  WebSocketService().connect();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BEMO App',
      home: const DashboardApp(),
      debugShowCheckedModeBanner: false,
    );
  }
}
