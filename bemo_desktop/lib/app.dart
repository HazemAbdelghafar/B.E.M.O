import 'screens/login.dart';
import 'screens/signup.dart';
import 'screens/dashboard.dart';
import 'screens/user_settings.dart';
import 'screens/getting_started.dart';
import 'screens/chat_history.dart';
import 'package:flutter/material.dart';

class BemoApp extends StatelessWidget {
  const BemoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BEMO Desktop',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(useMaterial3: true),
      initialRoute: '/signup',
      routes: {
        '/signup': (context) => SignupScreen(),
        '/login': (context) => const LoginScreen(),
        '/dashboard': (context) => const DashboardScreen(),
        '/getting-started': (context) => GettingStartedPage(),
        '/chat-history': (context) => const ChatHistoryScreen(),
        '/user-settings': (context) => const UserSettingsPage(),
      },
    );
  }
}
