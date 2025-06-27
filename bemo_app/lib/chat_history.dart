import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'bemo_sidebar.dart';
import 'user_settings.dart';
import 'dashboard.dart';

class ChatHistoryScreen extends StatefulWidget {
  const ChatHistoryScreen({Key? key}) : super(key: key);

  @override
  State<ChatHistoryScreen> createState() => _ChatHistoryScreenState();
}

class _ChatHistoryScreenState extends State<ChatHistoryScreen> {
  static const List<String> profileImages = [
    'assets/Images/bemo_profile1.png',
    'assets/Images/bemo_profile2.png',
    'assets/Images/bemo_profile3.png',
    'assets/Images/bemo_profile4.png',
    'assets/Images/bemo_profile5.png',
  ];
  late String currentProfileImage;
  late Timer _timer;
  bool _collapsed = false;

  // Placeholder chat messages
  final List<Map<String, dynamic>> chatMessages = [
    {
      'fromUser': true,
      'text': 'ADD "BUY GROCERIES" TO MY TASKS',
      'time': '10:00 AM',
    },
    {
      'fromUser': false,
      'text': 'GOT IT! "BUY GROCERIES" IS NOW ADDED TO YOUR TO-DO LIST 🙂',
      'time': '',
    },
    {
      'fromUser': true,
      'text': 'DO I HAVE ANY NEW EMAILS?',
      'time': '10:48 AM',
    },
    {
      'fromUser': false,
      'text': 'YOU HAVE 2 NEW EMAILS:\nFROM: DR. HANAN – "MEETING NOTES & SLIDES"\nFROM: AMAZON – "YOUR ORDER HAS SHIPPED"\nWOULD YOU LIKE ME TO READ ONE? 🙂',
      'time': '',
    },
    {
      'fromUser': true,
      'text': 'SHOW ME SOME BOOKS TO LEARN JAPANESE',
      'time': '3:24 PM',
    },
    {
      'fromUser': false,
      "text": "I HAVE FOUND 7 BOOKS ON LEARNING JAPANESE, CAN'T WAIT TO HEAR YOUR FIRST 'KONNICHIWA!' 😄",
      'time': '',
    },
    {
      'fromUser': true,
      "text": "WHAT'S THE CAPITAL OF NORWAY?",
      'time': '7:03 PM',
    },
  ];

  @override
  void initState() {
    super.initState();
    currentProfileImage = profileImages[Random().nextInt(profileImages.length)];
    _timer = Timer.periodic(const Duration(seconds: 30), (_) {
      setState(() {
        currentProfileImage = profileImages[Random().nextInt(profileImages.length)];
      });
    });
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  void _onSidebarSectionTap(BemoSection section) {
    if (section == BemoSection.chatHistory) return;
    if (section == BemoSection.dashboard) {
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (context) => const DashboardScreen(),
        ),
      );
      return;
    }
    if (section == BemoSection.settings) {
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (context) => const UserSettingsPage(),
        ),
      );
      return;
    }
    // Add navigation logic for other sections if needed
    // For now, do nothing or pop
    // Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    const double baseWidth = 1820;
    const double baseHeight = 980;
    final double sidebarWidth = _collapsed ? 70 : 300;
    return Scaffold(
      backgroundColor: const Color(0xFF2C2D30),
      body: Center(
        child: FittedBox(
          fit: BoxFit.contain,
          child: Container(
            width: baseWidth,
            height: baseHeight,
            decoration: BoxDecoration(
              color: const Color(0xFF191919),
              borderRadius: BorderRadius.circular(30),
            ),
            child: Stack(
              children: [
                // Sidebar
                Positioned(
                  left: 0,
                  top: 0,
                  bottom: 0,
                  child: BemoSidebar(
                    collapsed: _collapsed,
                    onToggle: () {
                      setState(() {
                        _collapsed = !_collapsed;
                      });
                    },
                    currentSection: BemoSection.chatHistory,
                    onSectionTap: _onSidebarSectionTap,
                    userName: 'Begad Tamim',
                  ),
                ),
                // Vertical divider
                Positioned(
                  left: sidebarWidth,
                  top: 100,
                  bottom: 0,
                  child: Container(
                    width: 2,
                    height: baseHeight - 100,
                    color: const Color(0xFF444444),
                  ),
                ),
                // Chat area with background
                Positioned(
                  left: sidebarWidth + 2,
                  right: 0,
                  top: 0,
                  bottom: 0,
                  child: Stack(
                    children: [
                      // Chat background
                      Positioned.fill(
                        child: ClipRRect(
                          borderRadius: const BorderRadius.only(
                            topRight: Radius.circular(30),
                            bottomRight: Radius.circular(30),
                          ),
                          child: Image.asset(
                            'assets/Images/Chat_history_Background.png',
                            fit: BoxFit.cover,
                          ),
                        ),
                      ),
                      // Top bar: black background, profile, BEMO text, status, and icons
                      Positioned(
                        left: 0,
                        right: 0,
                        top: 0,
                        child: Container(
                          height: 100,
                          decoration: const BoxDecoration(
                            color: Color(0xFF191919),
                            borderRadius: BorderRadius.only(
                              topRight: Radius.circular(30),
                              topLeft: Radius.circular(0), // left is handled by sidebar
                            ),
                          ),
                          child: Stack(
                            children: [
                              // Profile + BEMO + status (centered)
                              Align(
                                alignment: Alignment.center,
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    CircleAvatar(
                                      radius: 32,
                                      backgroundImage: AssetImage(currentProfileImage),
                                    ),
                                    const SizedBox(width: 18),
                                    Column(
                                      mainAxisAlignment: MainAxisAlignment.center,
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        const Text(
                                          'BEMO',
                                          style: TextStyle(
                                            color: Colors.white,
                                            fontSize: 28,
                                            fontFamily: 'Hyperion',
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                        const SizedBox(height: 4),
                                        Row(
                                          children: [
                                            Container(
                                              width: 10,
                                              height: 10,
                                              decoration: const BoxDecoration(
                                                color: Colors.green,
                                                shape: BoxShape.circle,
                                              ),
                                            ),
                                            const SizedBox(width: 6),
                                            const Text(
                                              'always online',
                                              style: TextStyle(
                                                color: Color.fromRGBO(255,255,255,0.5),
                                                fontSize: 14,
                                                fontFamily: 'Hyperion',
                                                fontWeight: FontWeight.w500,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                              // Top right icons
                              Positioned(
                                right: 40,
                                top: 26,
                                child: Row(
                                  children: [
                                    GestureDetector(
                                      onTap: () {},
                                      child: Image.asset(
                                        'assets/Images/search.png',
                                        width: 32,
                                        height: 32,
                                      ),
                                    ),
                                    const SizedBox(width: 16),
                                    GestureDetector(
                                      onTap: () {},
                                      child: Image.asset(
                                        'assets/Images/copy.png',
                                        width: 32,
                                        height: 32,
                                      ),
                                    ),
                                    const SizedBox(width: 16),
                                    GestureDetector(
                                      onTap: () {},
                                      child: Image.asset(
                                        'assets/Images/link.png',
                                        width: 32,
                                        height: 32,
                                      ),
                                    ),
                                    const SizedBox(width: 16),
                                    GestureDetector(
                                      onTap: () {},
                                      child: Image.asset(
                                        'assets/Images/popular.png',
                                        width: 32,
                                        height: 32,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      // Chat messages
                      Positioned.fill(
                        top: 150,
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 60.0, vertical: 32.0),
                          child: ListView.builder(
                            itemCount: chatMessages.length,
                            itemBuilder: (context, index) {
                              final msg = chatMessages[index];
                              final isUser = msg['fromUser'] as bool;
                              return Align(
                                alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                                child: Container(
                                  margin: const EdgeInsets.symmetric(vertical: 16),
                                  padding: const EdgeInsets.all(24),
                                  constraints: const BoxConstraints(maxWidth: 600),
                                  decoration: BoxDecoration(
                                    color: isUser ? const Color(0xFF0C4111) : const Color(0xFF281636),
                                    borderRadius: BorderRadius.only(
                                      topLeft: const Radius.circular(30),
                                      topRight: const Radius.circular(30),
                                      bottomLeft: isUser ? const Radius.circular(30) : const Radius.circular(0),
                                      bottomRight: isUser ? const Radius.circular(0) : const Radius.circular(30),
                                    ),
                                  ),
                                  child: Text(
                                    msg['text'],
                                    style: const TextStyle(
                                      color: Color(0xFFEFEFEF),
                                      fontSize: 20,
                                      fontFamily: 'Hyperion',
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
} 