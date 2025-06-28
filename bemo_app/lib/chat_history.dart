import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'bemo_sidebar.dart';
import 'user_settings.dart';
import 'dashboard.dart';
import 'package:intl/intl.dart';
import 'services/websocket_service.dart';
import 'package:flutter/widgets.dart';

class ChatHistoryScreen extends StatefulWidget {
  const ChatHistoryScreen({Key? key}) : super(key: key);

  @override
  State<ChatHistoryScreen> createState() => _ChatHistoryScreenState();
}

class _ChatHistoryScreenState extends State<ChatHistoryScreen> with TickerProviderStateMixin {
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
  bool _isConnected = false;
  final ScrollController _scrollController = ScrollController();
  late AnimationController _thinkingAnimationController;
  late Animation<double> _thinkingAnimation;

  @override
  void initState() {
    super.initState();
    currentProfileImage = profileImages[Random().nextInt(profileImages.length)];
    _timer = Timer.periodic(const Duration(seconds: 30), (_) {
      setState(() {
        currentProfileImage =
            profileImages[Random().nextInt(profileImages.length)];
      });
    });

    // Initialize connection status
    _isConnected = WebSocketService().isConnected;

    // Listen to new messages to trigger UI updates
    WebSocketService().messages.listen((msg) {
      setState(() {
        // Update connection status
        if (msg['type'] == 'connection_status') {
          _isConnected = msg['connected'] ?? false;
        }
        // This will trigger a rebuild when new messages arrive
      });
      
      // Start thinking animation if there's a thinking message
      if (WebSocketService().chatMessages.isNotEmpty && 
          WebSocketService().chatMessages.last['is_thinking'] == true) {
        _thinkingAnimationController.repeat();
      } else {
        _thinkingAnimationController.stop();
      }
      
      // Auto-scroll to bottom when new messages arrive
      Future.delayed(const Duration(milliseconds: 100), () {
        _scrollToBottom();
      });
    });

    _thinkingAnimationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    );
    _thinkingAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _thinkingAnimationController,
        curve: Curves.easeInOut,
      ),
    );
  }

  @override
  void dispose() {
    _timer.cancel();
    _scrollController.dispose();
    _thinkingAnimationController.dispose();
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

  // Method to scroll to bottom
  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    const double baseWidth = 1820;
    const double baseHeight = 980;
    final double sidebarWidth = _collapsed ? 70 : 300;
    final String todayDate =
        'Today, ' + DateFormat('MMMM d, y').format(DateTime.now());
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
                              topLeft: Radius.circular(0),
                            ),
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              Expanded(
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    CircleAvatar(
                                      radius: 32,
                                      backgroundImage:
                                          AssetImage(currentProfileImage),
                                    ),
                                    const SizedBox(width: 18),
                                    Column(
                                      mainAxisAlignment:
                                          MainAxisAlignment.center,
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
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
                                              decoration: BoxDecoration(
                                                color: _isConnected ? Colors.green : Colors.red,
                                                shape: BoxShape.circle,
                                              ),
                                            ),
                                            const SizedBox(width: 6),
                                            Text(
                                              _isConnected ? 'connected' : 'disconnected',
                                              style: const TextStyle(
                                                color: Color.fromRGBO(
                                                    255, 255, 255, 0.5),
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
                              Row(
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
                                  const SizedBox(width: 40),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                      // Chat messages
                      Positioned.fill(
                        top: 150,
                        child: Padding(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 60.0, vertical: 32.0),
                          child: Column(
                            children: [
                              // Day/date header
                              Align(
                                alignment: Alignment.topCenter,
                                child: Padding(
                                  padding: const EdgeInsets.only(
                                      top: 8.0, bottom: 8.0),
                                  child: Text(
                                    todayDate.toLowerCase(),
                                    style: const TextStyle(
                                      color: Color(0xFFEFEFEF),
                                      fontSize: 18,
                                      fontFamily: 'Hyperion',
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ),
                              Expanded(
                                child: WebSocketService().chatMessages.isEmpty
                                    ? Center(
                                        child: Column(
                                          mainAxisAlignment: MainAxisAlignment.center,
                                          children: [
                                            Icon(
                                              Icons.chat_bubble_outline,
                                              size: 64,
                                              color: Colors.grey[600],
                                            ),
                                            const SizedBox(height: 16),
                                            Text(
                                              'No messages yet',
                                              style: TextStyle(
                                                color: Colors.grey[600],
                                                fontSize: 18,
                                                fontFamily: 'Hyperion',
                                                fontWeight: FontWeight.w500,
                                              ),
                                            ),
                                            const SizedBox(height: 8),
                                            Text(
                                              _isConnected 
                                                  ? 'Start a conversation with BEMO'
                                                  : 'Connecting to BEMO...',
                                              style: TextStyle(
                                                color: Colors.grey[500],
                                                fontSize: 14,
                                                fontFamily: 'Hyperion',
                                                fontWeight: FontWeight.w400,
                                              ),
                                            ),
                                          ],
                                        ),
                                      )
                                    : ListView.builder(
                                        controller: _scrollController,
                                        itemCount:
                                            WebSocketService().chatMessages.length,
                                        itemBuilder: (context, index) {
                                          final msg =
                                              WebSocketService().chatMessages[index];
                                          final isUser = msg['fromUser'] as bool;
                                          
                                          // Skip empty messages
                                          final messageText = msg['text']?.toString().trim() ?? '';
                                          if (messageText.isEmpty) {
                                            return const SizedBox.shrink();
                                          }
                                          
                                          return Align(
                                            alignment: isUser
                                                ? Alignment.centerRight
                                                : Alignment.centerLeft,
                                            child: Column(
                                              crossAxisAlignment: isUser
                                                  ? CrossAxisAlignment.end
                                                  : CrossAxisAlignment.start,
                                              children: [
                                                Container(
                                                  margin: const EdgeInsets.symmetric(
                                                      vertical: 16),
                                                  padding: const EdgeInsets.all(24),
                                                  constraints: const BoxConstraints(
                                                      maxWidth: 600),
                                                  decoration: BoxDecoration(
                                                    color: isUser
                                                        ? const Color(0xFF0C4111)
                                                        : const Color(0xFF281636),
                                                    borderRadius: BorderRadius.only(
                                                      topLeft:
                                                          const Radius.circular(30),
                                                      topRight:
                                                          const Radius.circular(30),
                                                      bottomLeft: isUser
                                                          ? const Radius.circular(30)
                                                          : const Radius.circular(0),
                                                      bottomRight: isUser
                                                          ? const Radius.circular(0)
                                                          : const Radius.circular(30),
                                                    ),
                                                  ),
                                                  child: Text(
                                                    messageText.toLowerCase(),
                                                    style: TextStyle(
                                                      color: (!isUser &&
                                                              msg['is_server_error'] ==
                                                                  true)
                                                          ? Colors.red
                                                          : const Color(0xFFEFEFEF),
                                                      fontSize: 20,
                                                      fontFamily: 'Hyperion',
                                                      fontWeight: FontWeight.bold,
                                                    ),
                                                  ),
                                                ),
                                                if (!isUser &&
                                                    msg['is_learning_resources'] == true)
                                                  Padding(
                                                    padding: const EdgeInsets.only(
                                                        top: 4.0,
                                                        left: 8.0,
                                                        right: 8.0),
                                                    child: Image.asset(
                                                      'assets/Images/link.png',
                                                      width: 28,
                                                      height: 28,
                                                    ),
                                                  ),
                                                if (!isUser &&
                                                    msg['is_thinking'] == true)
                                                  Padding(
                                                    padding: const EdgeInsets.only(
                                                        top: 4.0,
                                                        left: 8.0,
                                                        right: 8.0),
                                                    child: Row(
                                                      mainAxisSize: MainAxisSize.min,
                                                      children: [
                                                        AnimatedBuilder(
                                                          animation: _thinkingAnimation,
                                                          builder: (context, child) {
                                                            return Container(
                                                              width: 8,
                                                              height: 8,
                                                              decoration: BoxDecoration(
                                                                color: Colors.grey[400]?.withOpacity(
                                                                  0.3 + (_thinkingAnimation.value * 0.7)
                                                                ),
                                                                shape: BoxShape.circle,
                                                              ),
                                                            );
                                                          },
                                                        ),
                                                        const SizedBox(width: 4),
                                                        AnimatedBuilder(
                                                          animation: _thinkingAnimation,
                                                          builder: (context, child) {
                                                            return Container(
                                                              width: 8,
                                                              height: 8,
                                                              decoration: BoxDecoration(
                                                                color: Colors.grey[400]?.withOpacity(
                                                                  0.3 + (_thinkingAnimation.value * 0.7)
                                                                ),
                                                                shape: BoxShape.circle,
                                                              ),
                                                            );
                                                          },
                                                        ),
                                                        const SizedBox(width: 4),
                                                        AnimatedBuilder(
                                                          animation: _thinkingAnimation,
                                                          builder: (context, child) {
                                                            return Container(
                                                              width: 8,
                                                              height: 8,
                                                              decoration: BoxDecoration(
                                                                color: Colors.grey[400]?.withOpacity(
                                                                  0.3 + (_thinkingAnimation.value * 0.7)
                                                                ),
                                                                shape: BoxShape.circle,
                                                              ),
                                                            );
                                                          },
                                                        ),
                                                      ],
                                                    ),
                                                  ),
                                                Padding(
                                                  padding: const EdgeInsets.only(
                                                      top: 2, left: 8, right: 8),
                                                  child: Text(
                                                    DateFormat('hh:mm a').format(
                                                        DateTime.tryParse(
                                                                msg['time']) ??
                                                            DateTime.now()),
                                                    style: const TextStyle(
                                                      color: Color(0xFFB0B0B0),
                                                      fontSize: 13,
                                                      fontFamily: 'Hyperion',
                                                      fontWeight: FontWeight.w400,
                                                    ),
                                                  ),
                                                ),
                                              ],
                                            ),
                                          );
                                        },
                                      ),
                              ),
                            ],
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
