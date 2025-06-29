import 'package:flutter/material.dart';
import 'user_settings.dart';
import 'chat_history.dart';
import '../widgets/bemo_sidebar.dart';
import '../services/websocket_service.dart';
import '../services/firebase_user_service.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  bool _collapsed = false;
  static const double expandedWidth = 300;
  static const double collapsedWidth = 70;

  void _toggleSidebar() {
    setState(() {
      _collapsed = !_collapsed;
    });
  }

  @override
  Widget build(BuildContext context) {
    const double baseWidth = 1820;
    const double baseHeight = 980;
    final double sidebarWidth = _collapsed ? collapsedWidth : expandedWidth;
    final double dividerLeft = sidebarWidth;
    final double mainContentLeft = sidebarWidth + 2;

    final Map<String, dynamic> arguments =
        ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;
    final String uid = arguments['uid']!;
    final String idToken = arguments['idToken']!;
    final String email = arguments['email']!;

    // Check connection status
    final bool isConnected = WebSocketService().isConnected;
    print('Dashboard - WebSocket connected: $isConnected');

    void onSidebarSectionTap(BemoSection section) {
      if (section == BemoSection.dashboard) return;
      if (section == BemoSection.chatHistory) {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => const ChatHistoryScreen(),
            settings: RouteSettings(
              arguments: {'uid': uid, 'idToken': idToken, 'email': email},
            ),
          ),
        );
        return;
      }
      if (section == BemoSection.settings) {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => const UserSettingsPage(),
            settings: RouteSettings(
              arguments: {'uid': uid, 'idToken': idToken, 'email': email},
            ),
          ),
        );
        return;
      }
    }

    return FutureBuilder(
      future: FirebaseUserService().fetchUserData(uid: uid, idToken: idToken),
      builder: (context, snapshot) {
        String title = 'Eng.';
        String lastName = 'Abdelghafar';
        String preferredName = 'Zoma';
        if (snapshot.hasData) {
          title = snapshot.data!['title'] ?? 'Eng.';
          lastName = snapshot.data!['last_name'] ?? 'Abdelghafar';
          preferredName = snapshot.data!['preferred_name'] ?? 'Zoma';
        }

        return Scaffold(
          backgroundColor: const Color(0xFF2C2D30),
          body: Center(
            child: FittedBox(
              fit: BoxFit.contain,
              child: Container(
                width: baseWidth,
                height: baseHeight,
                decoration: BoxDecoration(
                  color: Color(0xFF191919), // black background
                  borderRadius: BorderRadius.circular(30),
                ),
                child: Stack(
                  children: [
                    // Sidebar (left)
                    Positioned(
                      left: 0,
                      top: 0,
                      bottom: 0,
                      child: BemoSidebar(
                        collapsed: _collapsed,
                        onToggle: _toggleSidebar,
                        currentSection: BemoSection.dashboard,
                        onSectionTap: onSidebarSectionTap,
                        userName: preferredName,
                      ),
                    ),
                    // Vertical separator between sidebar and center
                    Positioned(
                      left: dividerLeft,
                      top: 0,
                      bottom: 0,
                      child: Container(
                        width: 2,
                        height: 980,
                        color: Color(0xFF444444),
                      ),
                    ),
                    // Notification panel (right)
                    Positioned(
                      right: 12,
                      top: 20,
                      bottom: 20,
                      child: Container(
                        width: 350,
                        height: 980,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(32),
                          boxShadow: [
                            BoxShadow(
                              color: Color.fromRGBO(0, 0, 0, 0.1),
                              blurRadius: 16,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Padding(
                          padding: const EdgeInsets.all(32.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              const Text(
                                'recent',
                                style: TextStyle(
                                  fontFamily: 'Hyperion',
                                  fontWeight: FontWeight.bold,
                                  fontSize: 22,
                                  color: Colors.black,
                                  letterSpacing: 1.2,
                                ),
                                textAlign: TextAlign.center,
                              ),
                              const Text(
                                'notifications',
                                style: TextStyle(
                                  fontFamily: 'Hyperion',
                                  fontWeight: FontWeight.bold,
                                  fontSize: 22,
                                  color: Colors.black,
                                  letterSpacing: 1.2,
                                ),
                                textAlign: TextAlign.center,
                              ),
                              const SizedBox(height: 4),
                              Container(
                                width: 60,
                                height: 2,
                                color: Color.fromRGBO(0, 0, 0, 0.26),
                                margin: const EdgeInsets.symmetric(vertical: 8),
                              ),
                              _NotificationItem(
                                iconAsset: 'assets/images/Notification.png',
                                title: 'learning resources',
                                subtitle:
                                    'resources on "python programming language" has been sent to your email',
                                time: 'JUST NOW',
                              ),
                              const SizedBox(height: 6),
                              _NotificationItem(
                                iconAsset: 'assets/images/At sign.png',
                                title: 'linkedin',
                                subtitle:
                                    'companies like systems limited egypt and others in your network have been sent to your email',
                                time: '2 MINS AGO',
                              ),
                              const SizedBox(height: 6),
                              _NotificationItem(
                                iconAsset: 'assets/images/To Do List.png',
                                title: 'water the plants',
                                subtitle:
                                    '5 DROPS OF MINERAL WATER DUE IN 19 MINS',
                                time: '17 MINS AGO',
                              ),
                              const SizedBox(height: 6),
                              _NotificationItem(
                                iconAsset: 'assets/images/Cloud Folder.png',
                                title: 'cloudshell',
                                subtitle:
                                    'deletion notice for your google cloud shell home directory',
                                time: '2 HOURS AGO',
                              ),
                              const Spacer(),
                              Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceEvenly,
                                children: [
                                  _NotifActionIcon(
                                    iconAsset: 'assets/images/Door Hanger.png',
                                    label: 'do not disturb: off',
                                  ),
                                  _NotifActionIcon(
                                    iconAsset: 'assets/images/Erase.png',
                                    label: 'clear notifications',
                                  ),
                                  _NotifActionIcon(
                                    iconAsset: 'assets/images/Notification.png',
                                    label: 'all notifications',
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    // Main content (center)
                    AnimatedPositioned(
                      duration: const Duration(milliseconds: 300),
                      left:
                          mainContentLeft +
                          28, // move a little more right for visual balance
                      right: 347,
                      top: 0,
                      bottom: 0,
                      child: Stack(
                        children: [
                          // Greeting
                          Positioned(
                            left: 29,
                            top: 59,
                            child: SizedBox(
                              width: 700,
                              height: 88,
                              child: Stack(
                                children: [
                                  Positioned(
                                    left: 0,
                                    top: 0,
                                    child: Text(
                                      'hello $title $lastName'.toLowerCase(),
                                      style: TextStyle(
                                        color: Color(0xFFEFEFEF),
                                        fontSize: 40,
                                        fontFamily: 'Hyperion',
                                        fontWeight: FontWeight.bold,
                                        height: 1,
                                      ),
                                    ),
                                  ),
                                  Positioned(
                                    left: 0,
                                    top: 60,
                                    child: Text(
                                      'good afternoon!',
                                      style: TextStyle(
                                        color: Color.fromRGBO(
                                          255,
                                          255,
                                          255,
                                          0.8,
                                        ),
                                        fontSize: 24,
                                        fontFamily: 'Hyperion',
                                        fontWeight: FontWeight.bold,
                                        height: 1,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          // Featured Section
                          Positioned(
                            left: 29,
                            top: 185,
                            child: SizedBox(
                              width: 980,
                              height: 353,
                              child: Stack(
                                children: [
                                  Positioned(
                                    left: 0,
                                    top: 62,
                                    child: SizedBox(
                                      width: 980,
                                      height: 291,
                                      child: Stack(
                                        children: [
                                          Positioned(
                                            left: 0,
                                            top: 0,
                                            child: Container(
                                              width: 980,
                                              height: 290,
                                              decoration: BoxDecoration(
                                                borderRadius:
                                                    BorderRadius.circular(36),
                                              ),
                                              child: ClipRRect(
                                                borderRadius:
                                                    BorderRadius.circular(36),
                                                child: Opacity(
                                                  opacity: 0.95,
                                                  child: Image.asset(
                                                    'assets/images/mail_task.png',
                                                    width: 1016,
                                                    height: 290,
                                                    fit: BoxFit.cover,
                                                  ),
                                                ),
                                              ),
                                            ),
                                          ),
                                          // Featured text
                                          Positioned(
                                            left: 19,
                                            top: 239,
                                            child: SizedBox(
                                              width: 585,
                                              child: Text(
                                                "try saying: hey bemo, read out my unread emails",
                                                style: TextStyle(
                                                  color: Color(0xFFEFEFEF),
                                                  fontSize: 20,
                                                  fontFamily: 'Hyperion',
                                                  fontWeight: FontWeight.bold,
                                                  height: 1,
                                                ),
                                              ),
                                            ),
                                          ),
                                          Positioned(
                                            left: 19,
                                            top: 22,
                                            child: SizedBox(
                                              width: 367.25,
                                              child: Text.rich(
                                                TextSpan(
                                                  children: [
                                                    TextSpan(
                                                      text:
                                                          'bemo mail assistant:\n',
                                                      style: TextStyle(
                                                        color: Color(
                                                          0xFFEFEFEF,
                                                        ),
                                                        fontSize: 28,
                                                        fontFamily: 'Hyperion',
                                                        fontWeight:
                                                            FontWeight.bold,
                                                        height: 1,
                                                      ),
                                                    ),
                                                    TextSpan(
                                                      text:
                                                          'hands-free email access',
                                                      style: TextStyle(
                                                        color: Color(
                                                          0xFFEFEFEF,
                                                        ),
                                                        fontSize: 24,
                                                        fontFamily: 'Hyperion',
                                                        fontWeight:
                                                            FontWeight.bold,
                                                        height: 1,
                                                      ),
                                                    ),
                                                  ],
                                                ),
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),
                                  // Featured label
                                  Positioned(
                                    left: 14,
                                    top: 0,
                                    child: SizedBox(
                                      width: 215,
                                      child: Text(
                                        'featured',
                                        style: TextStyle(
                                          color: Color(0xFFEFEFEF),
                                          fontSize: 32,
                                          fontFamily: 'Hyperion',
                                          fontWeight: FontWeight.bold,
                                          height: 1,
                                        ),
                                      ),
                                    ),
                                  ),
                                  // Dots (carousel indicators)
                                  Positioned(
                                    left: 839.92,
                                    top: 321.14,
                                    child: Container(
                                      width: 19.72,
                                      height: 19.72,
                                      decoration: BoxDecoration(
                                        color: Color(0xAFEFEFEF),
                                        shape: BoxShape.circle,
                                        border: Border.all(
                                          width: 3,
                                          color: Color(0xFFEFEFEF),
                                        ),
                                      ),
                                    ),
                                  ),
                                  Positioned(
                                    left: 907.96,
                                    top: 321.14,
                                    child: Container(
                                      width: 19.72,
                                      height: 19.72,
                                      decoration: BoxDecoration(
                                        color: Color(0xAFEFEFEF),
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                  ),
                                  Positioned(
                                    left: 941.98,
                                    top: 321.14,
                                    child: Container(
                                      width: 19.72,
                                      height: 19.72,
                                      decoration: BoxDecoration(
                                        color: Color(0xAFEFEFEF),
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                  ),
                                  Positioned(
                                    left: 873.92,
                                    top: 321.14,
                                    child: Container(
                                      width: 19.72,
                                      height: 19.72,
                                      decoration: BoxDecoration(
                                        color: Color(0xAFEFEFEF),
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          // Recent Projects Section
                          Positioned(
                            left: 29,
                            top: 582,
                            child: SizedBox(
                              width: 980,
                              height: 352,
                              child: Stack(
                                children: [
                                  // Project Card 1
                                  Positioned(
                                    left: 0,
                                    top: 62,
                                    child: Container(
                                      width: 290,
                                      height: 290,
                                      decoration: BoxDecoration(
                                        color: Color(0xFF241430),
                                        borderRadius: BorderRadius.circular(20),
                                      ),
                                      child: Stack(
                                        children: [
                                          Positioned(
                                            left: 15,
                                            top: 29,
                                            child: SizedBox(
                                              width: 275,
                                              child: Text(
                                                'nflx stock\nprice prediction',
                                                style: TextStyle(
                                                  color: Color(0xFFEFEFEF),
                                                  fontSize: 24,
                                                  fontFamily: 'Hyperion',
                                                  fontWeight: FontWeight.bold,
                                                  height: 1,
                                                ),
                                              ),
                                            ),
                                          ),
                                          Positioned(
                                            left: 15,
                                            top: 208,
                                            child: SizedBox(
                                              width: 265,
                                              child: Text(
                                                'last opened: 4 hours ago',
                                                style: TextStyle(
                                                  color: Color(0xFFEFEFEF),
                                                  fontSize: 15,
                                                  fontFamily: 'Hyperion',
                                                  fontWeight: FontWeight.bold,
                                                  height: 1,
                                                ),
                                              ),
                                            ),
                                          ),
                                          Positioned(
                                            left: 15,
                                            top: 247,
                                            child: SizedBox(
                                              width: 96,
                                              height: 25,
                                              child: Text(
                                                'open with:',
                                                style: TextStyle(
                                                  color: Color(0xFFEFEFEF),
                                                  fontSize: 16,
                                                  fontFamily: 'Hyperion',
                                                  fontWeight: FontWeight.bold,
                                                  height: 1,
                                                ),
                                              ),
                                            ),
                                          ),
                                          Positioned(
                                            left: 15,
                                            top: 187,
                                            child: SizedBox(
                                              width: 265,
                                              child: Text(
                                                'size on disk: 98.3 kb',
                                                style: TextStyle(
                                                  color: Color(0xFFEFEFEF),
                                                  fontSize: 15,
                                                  fontFamily: 'Hyperion',
                                                  fontWeight: FontWeight.bold,
                                                  height: 1,
                                                ),
                                              ),
                                            ),
                                          ),
                                          // Add icons as needed using Positioned
                                        ],
                                      ),
                                    ),
                                  ),
                                  // Project Card 2
                                  Positioned(
                                    left: 345,
                                    top: 62,
                                    child: Container(
                                      width: 290,
                                      height: 290,
                                      decoration: BoxDecoration(
                                        color: Color(0xFF082C0C),
                                        borderRadius: BorderRadius.circular(20),
                                      ),
                                      child: Stack(
                                        children: [
                                          Positioned(
                                            left: 15,
                                            top: 29,
                                            child: SizedBox(
                                              width: 275,
                                              child: Text(
                                                "reimagining\npear's logo",
                                                style: TextStyle(
                                                  color: Color(0xFFEFEFEF),
                                                  fontSize: 24,
                                                  fontFamily: 'Hyperion',
                                                  fontWeight: FontWeight.bold,
                                                  height: 1,
                                                ),
                                              ),
                                            ),
                                          ),
                                          Positioned(
                                            left: 15,
                                            top: 208,
                                            child: SizedBox(
                                              width: 265,
                                              child: Text(
                                                'last opened: 2 days ago',
                                                style: TextStyle(
                                                  color: Color(0xFFEFEFEF),
                                                  fontSize: 15,
                                                  fontFamily: 'Hyperion',
                                                  fontWeight: FontWeight.bold,
                                                  height: 1,
                                                ),
                                              ),
                                            ),
                                          ),
                                          Positioned(
                                            left: 15,
                                            top: 247,
                                            child: SizedBox(
                                              width: 96,
                                              height: 25,
                                              child: Text(
                                                'open with:',
                                                style: TextStyle(
                                                  color: Color(0xFFEFEFEF),
                                                  fontSize: 16,
                                                  fontFamily: 'Hyperion',
                                                  fontWeight: FontWeight.bold,
                                                  height: 1,
                                                ),
                                              ),
                                            ),
                                          ),
                                          Positioned(
                                            left: 15,
                                            top: 187,
                                            child: SizedBox(
                                              width: 265,
                                              child: Text(
                                                'size on disk: 10.2 mb',
                                                style: TextStyle(
                                                  color: Color(0xFFEFEFEF),
                                                  fontSize: 15,
                                                  fontFamily: 'Hyperion',
                                                  fontWeight: FontWeight.bold,
                                                  height: 1,
                                                ),
                                              ),
                                            ),
                                          ),
                                          // Add icons as needed using Positioned
                                        ],
                                      ),
                                    ),
                                  ),
                                  // Project Card 3
                                  Positioned(
                                    left: 690,
                                    top: 62,
                                    child: Container(
                                      width: 290,
                                      height: 290,
                                      decoration: BoxDecoration(
                                        color: Color(0xFF321500),
                                        borderRadius: BorderRadius.circular(20),
                                      ),
                                      child: Stack(
                                        children: [
                                          Positioned(
                                            left: 15,
                                            top: 29,
                                            child: SizedBox(
                                              width: 275,
                                              child: Text(
                                                "designing\nbemo's body",
                                                style: TextStyle(
                                                  color: Color(0xFFEFEFEF),
                                                  fontSize: 24,
                                                  fontFamily: 'Hyperion',
                                                  fontWeight: FontWeight.bold,
                                                  height: 1,
                                                ),
                                              ),
                                            ),
                                          ),
                                          Positioned(
                                            left: 15,
                                            top: 208,
                                            child: SizedBox(
                                              width: 265,
                                              child: Text(
                                                'last opened: 1 month ago',
                                                style: TextStyle(
                                                  color: Color(0xFFEFEFEF),
                                                  fontSize: 15,
                                                  fontFamily: 'Hyperion',
                                                  fontWeight: FontWeight.bold,
                                                  height: 1,
                                                ),
                                              ),
                                            ),
                                          ),
                                          Positioned(
                                            left: 15,
                                            top: 247,
                                            child: SizedBox(
                                              width: 96,
                                              height: 25,
                                              child: Text(
                                                'open with:',
                                                style: TextStyle(
                                                  color: Color(0xFFEFEFEF),
                                                  fontSize: 16,
                                                  fontFamily: 'Hyperion',
                                                  fontWeight: FontWeight.bold,
                                                  height: 1,
                                                ),
                                              ),
                                            ),
                                          ),
                                          Positioned(
                                            left: 15,
                                            top: 187,
                                            child: SizedBox(
                                              width: 265,
                                              child: Text(
                                                'size on disk: 0.8 gb',
                                                style: TextStyle(
                                                  color: Color(0xFFEFEFEF),
                                                  fontSize: 15,
                                                  fontFamily: 'Hyperion',
                                                  fontWeight: FontWeight.bold,
                                                  height: 1,
                                                ),
                                              ),
                                            ),
                                          ),
                                          // Add icons as needed using Positioned
                                        ],
                                      ),
                                    ),
                                  ),
                                  // Recent Projects label
                                  Positioned(
                                    left: 14,
                                    top: 0,
                                    child: Text(
                                      'recent projects',
                                      style: TextStyle(
                                        color: Color(0xFFEFEFEF),
                                        fontSize: 32,
                                        fontFamily: 'Hyperion',
                                        fontWeight: FontWeight.bold,
                                        height: 1,
                                      ),
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
      },
    );
  }
}

class _NotificationItem extends StatelessWidget {
  final String iconAsset;
  final String title;
  final String subtitle;
  final String time;
  const _NotificationItem({
    required this.iconAsset,
    required this.title,
    required this.subtitle,
    required this.time,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: const BoxDecoration(
              color: Color(0xFF2C2D30),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Image.asset(iconAsset, height: 22, color: Colors.white),
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontFamily: 'Hyperion',
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                    color: Colors.black,
                  ),
                ),
                Text(
                  subtitle,
                  style: const TextStyle(
                    fontWeight: FontWeight.w400,
                    fontSize: 11,
                    color: Colors.black54,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Text(
            time,
            style: const TextStyle(
              fontWeight: FontWeight.w400,
              fontSize: 10,
              color: Colors.black45,
            ),
          ),
        ],
      ),
    );
  }
}

class _NotifActionIcon extends StatelessWidget {
  final String iconAsset;
  final String label;
  const _NotifActionIcon({required this.iconAsset, required this.label});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: Color.fromRGBO(0, 0, 0, 0.85),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Center(
            child: Image.asset(iconAsset, height: 28, color: Colors.white),
          ),
        ),
        const SizedBox(height: 6),
        SizedBox(
          width: 90,
          child: Text(
            label,
            style: const TextStyle(
              color: Colors.black,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              fontFamily: 'Hyperion',
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}
