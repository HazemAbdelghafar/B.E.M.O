import 'package:flutter/material.dart';
import 'user_settings.dart';

class DashboardApp extends StatelessWidget {
  const DashboardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BEMO App',
      theme: ThemeData(
        fontFamily: 'Hyperion',
        scaffoldBackgroundColor: const Color(0xFF2C2D30),
        textTheme: Theme.of(context).textTheme.apply(
              fontFamily: 'Hyperion',
              bodyColor: Colors.white,
              displayColor: Colors.white,
            ),
      ),
      home: const DashboardScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

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
    final double sidebarWidth = _collapsed ? collapsedWidth : expandedWidth;
    final double dividerLeft = sidebarWidth;
    final double mainContentLeft = sidebarWidth + 2;
    return Scaffold(
      backgroundColor: const Color(0xFF2C2D30),
      body: Center(
        child: Container(
          width: 1820,
          height: 980,
          decoration: BoxDecoration(
            color: const Color(0xFF191919),
            borderRadius: BorderRadius.circular(30),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.25),
                blurRadius: 30,
                offset: const Offset(0, 8),
                spreadRadius: 15,
              ),
            ],
          ),
          child: Stack(
            children: [
              // Sidebar (left)
              AnimatedPositioned(
                duration: const Duration(milliseconds: 300),
                left: 0,
                top: 0,
                bottom: 0,
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  width: sidebarWidth,
                  height: 980,
                  decoration: const BoxDecoration(
                    color: Color(0xFF191919),
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(30),
                      bottomLeft: Radius.circular(30),
                    ),
                  ),
                  child: Column(
                    children: [
                      const SizedBox(height: 48),
                      GestureDetector(
                        onTap: _toggleSidebar,
                        child: Container(
                          width: _collapsed ? 48 : 200,
                          height: 60,
                          alignment: Alignment.center,
                          child: _collapsed
                              ? Image.asset(
                                  'assets/images/Robot - Inverted 1.png',
                                  fit: BoxFit.contain,
                                  height: 48,
                                )
                              : Image.asset(
                                  'assets/images/Logo 2 - Transparent Inverted 1 1.png',
                                  fit: BoxFit.contain,
                                  height: 48,
                                ),
                        ),
                      ),
                      if (!_collapsed) ...[
                        const SizedBox(height: 48),
                        _SidebarNav(
                            iconAsset: 'assets/images/Idea.png',
                            label: 'PROJECTS'),
                        const SizedBox(height: 8),
                        _SidebarNav(
                            iconAsset: 'assets/images/At sign.png',
                            label: 'E-MAIL'),
                        const SizedBox(height: 8),
                        _SidebarNav(
                            iconAsset: 'assets/images/To Do List.png',
                            label: 'TASKS'),
                        const SizedBox(height: 8),
                        _SidebarNav(
                            iconAsset: 'assets/images/Calendar 28.png',
                            label: 'CALENDAR'),
                        const SizedBox(height: 8),
                        _SidebarNav(
                            iconAsset: 'assets/images/Cloud Folder.png',
                            label: 'DRIVE'),
                        const SizedBox(height: 8),
                        _SidebarNav(
                            iconAsset:
                                'assets/images/Smart Home Connection.png',
                            label: 'SMART HOME'),
                        const SizedBox(height: 8),
                        _SidebarNav(
                            iconAsset: 'assets/images/Chat.png',
                            label: 'CHAT HISTORY'),
                        const SizedBox(height: 8),
                        _SidebarNav(
                            iconAsset: 'assets/images/Notification.png',
                            label: 'NOTIFICATIONS'),
                        const SizedBox(height: 8),
                        _SidebarNav(
                          iconAsset: 'assets/images/Control Panel.png',
                          label: 'SETTINGS',
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                  builder: (context) =>
                                      const UserSettingsPage()),
                            );
                          },
                        ),
                      ] else ...[
                        const SizedBox(height: 32),
                        _SidebarIconOnly(iconAsset: 'assets/images/Idea.png'),
                        const SizedBox(height: 16),
                        _SidebarIconOnly(
                            iconAsset: 'assets/images/At sign.png'),
                        const SizedBox(height: 16),
                        _SidebarIconOnly(
                            iconAsset: 'assets/images/To Do List.png'),
                        const SizedBox(height: 16),
                        _SidebarIconOnly(
                            iconAsset: 'assets/images/Calendar 28.png'),
                        const SizedBox(height: 16),
                        _SidebarIconOnly(
                            iconAsset: 'assets/images/Cloud Folder.png'),
                        const SizedBox(height: 16),
                        _SidebarIconOnly(
                            iconAsset:
                                'assets/images/Smart Home Connection.png'),
                        const SizedBox(height: 16),
                        _SidebarIconOnly(iconAsset: 'assets/images/Chat.png'),
                        const SizedBox(height: 16),
                        _SidebarIconOnly(
                            iconAsset: 'assets/images/Notification.png'),
                        const SizedBox(height: 16),
                        _SidebarIconOnly(
                          iconAsset: 'assets/images/Control Panel.png',
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                  builder: (context) =>
                                      const UserSettingsPage()),
                            );
                          },
                        ),
                      ],
                      const Spacer(),
                      Padding(
                        padding: const EdgeInsets.only(bottom: 32.0),
                        child: _collapsed
                            ? Center(
                                child: CircleAvatar(
                                  radius: 28,
                                  backgroundImage: AssetImage(
                                      'assets/images/Robot - Inverted 1.png'),
                                ),
                              )
                            : Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  CircleAvatar(
                                    radius: 28,
                                    backgroundImage: AssetImage(
                                        'assets/images/Robot - Inverted 1.png'),
                                  ),
                                  const SizedBox(width: 16),
                                  Text(
                                    'Begad Tamim',
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16,
                                      color: Colors.white.withOpacity(0.7),
                                    ),
                                  ),
                                ],
                              ),
                      ),
                    ],
                  ),
                ),
              ),
              // Vertical separator between sidebar and center
              AnimatedPositioned(
                duration: const Duration(milliseconds: 300),
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
                        color: Colors.black.withOpacity(0.1),
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
                          'RECENT',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 22,
                            color: Colors.black,
                            letterSpacing: 1.2,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const Text(
                          'NOTIFICATIONS',
                          style: TextStyle(
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
                          color: Colors.black26,
                          margin: const EdgeInsets.symmetric(vertical: 8),
                        ),
                        _NotificationItem(
                          iconAsset: 'assets/images/Notification.png',
                          title: 'LEARNING RESOURCES',
                          subtitle:
                              'RESOURCES ON "PYTHON PROGRAMMING LANGUAGE" HAS BEEN S...',
                          time: 'JUST NOW',
                        ),
                        const SizedBox(height: 6),
                        _NotificationItem(
                          iconAsset: 'assets/images/At sign.png',
                          title: 'LINKEDIN',
                          subtitle:
                              'COMPANIES LIKE SYSTEMS LIMITED EGYPT AND OTHERS IN YOUR NETWOR...',
                          time: '2 MINS AGO',
                        ),
                        const SizedBox(height: 6),
                        _NotificationItem(
                          iconAsset: 'assets/images/To Do List.png',
                          title: 'WATER THE PLANTS',
                          subtitle: '5 DROPS OF MINERAL WATER DUE IN 19 MINS',
                          time: '17 MINS AGO',
                        ),
                        const SizedBox(height: 6),
                        _NotificationItem(
                          iconAsset: 'assets/images/Cloud Folder.png',
                          title: 'CLOUDSHELL',
                          subtitle:
                              'DELETION NOTICE FOR YOUR GOOGLE CLOUD SHELL HOME DIRECTORY',
                          time: '2 HOURS AGO',
                        ),
                        const Spacer(),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            _NotifActionIcon(
                                iconAsset: 'assets/images/Door Hanger.png',
                                label: 'DO NOT DISTURB: OFF'),
                            _NotifActionIcon(
                                iconAsset: 'assets/images/Erase.png',
                                label: 'CLEAR NOTIFICATIONS'),
                            _NotifActionIcon(
                                iconAsset: 'assets/images/Notification.png',
                                label: 'ALL NOTIFICATIONS'),
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
                left: mainContentLeft +
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
                      child: Container(
                        width: 560,
                        height: 88,
                        child: Stack(
                          children: [
                            Positioned(
                              left: 0,
                              top: 0,
                              child: Text(
                                'HELLO ENG. BEGAD',
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
                                'GOOD AFTERNOON!',
                                style: TextStyle(
                                  color: Color(0x8CEFEFEF),
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
                      child: Container(
                        width: 980,
                        height: 353,
                        child: Stack(
                          children: [
                            Positioned(
                              left: 0,
                              top: 62,
                              child: Container(
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
                                        child: Stack(
                                          children: [
                                            Positioned(
                                              left: 0,
                                              top: 0,
                                              child: ClipRRect(
                                                borderRadius:
                                                    BorderRadius.circular(20),
                                                child: Opacity(
                                                  opacity: 0.7,
                                                  child: Image.asset(
                                                    'assets/images/mail_task.png',
                                                    width: 1016,
                                                    height: 290,
                                                    fit: BoxFit.cover,
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
                                                  "TRY SAYING: 'HEY BEMO, READ OUT MY UNREAD EMAILS'",
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
                                                            'BEMO MAILASSIST:\n',
                                                        style: TextStyle(
                                                          color:
                                                              Color(0xFFEFEFEF),
                                                          fontSize: 28,
                                                          fontFamily:
                                                              'Hyperion',
                                                          fontWeight:
                                                              FontWeight.bold,
                                                          height: 1,
                                                        ),
                                                      ),
                                                      TextSpan(
                                                        text:
                                                            'HANDS-FREE EMAIL ACCESS',
                                                        style: TextStyle(
                                                          color:
                                                              Color(0xFFEFEFEF),
                                                          fontSize: 24,
                                                          fontFamily:
                                                              'Hyperion',
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
                                  'FEATURED',
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
                                      width: 3, color: Color(0xFFEFEFEF)),
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
                      child: Container(
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
                                          'NFLX STOCK\nPRICE PREDICTION',
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
                                          'LAST OPENED: 4 HOURS AGO',
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
                                          'OPEN WITH:',
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
                                          'SIZE ON DISK: 98.3 KB',
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
                                          "REIMAGINING\nPEAR'S LOGO",
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
                                          'LAST OPENED: 2 DAYS AGO',
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
                                          'OPEN WITH:',
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
                                          'SIZE ON DISK: 10.2 MB',
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
                                          "DESIGNING\nBEMO'S BODY",
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
                                          'LAST OPENED: 1 MONTH AGO',
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
                                          'OPEN WITH:',
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
                                          'SIZE ON DISK: 0.8 GB',
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
                                'RECENT PROJECTS',
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
    );
  }
}

class _SidebarNav extends StatelessWidget {
  final String? iconAsset;
  final String label;
  final VoidCallback? onTap;
  const _SidebarNav({this.iconAsset, required this.label, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 10.0, horizontal: 32.0),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.start,
          children: [
            if (iconAsset != null)
              Image.asset(iconAsset!, height: 28, color: Colors.white),
            const SizedBox(width: 22),
            Text(
              label,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 18,
                color: Colors.white,
                letterSpacing: 1.2,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _NotificationItem extends StatelessWidget {
  final String iconAsset;
  final String title;
  final String subtitle;
  final String time;
  const _NotificationItem(
      {required this.iconAsset,
      required this.title,
      required this.subtitle,
      required this.time});

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
            color: Colors.black.withOpacity(0.85),
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

// Sidebar icon only widget for collapsed state
class _SidebarIconOnly extends StatelessWidget {
  final String iconAsset;
  final VoidCallback? onTap;
  const _SidebarIconOnly({required this.iconAsset, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8.0),
        child: Center(
          child: Image.asset(iconAsset, height: 28, color: Colors.white),
        ),
      ),
    );
  }
}
