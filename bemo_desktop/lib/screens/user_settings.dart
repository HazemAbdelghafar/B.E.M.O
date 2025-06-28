import 'package:flutter/material.dart';

//Todo: Display user data from firebase
//Todo: Implement function to update user data in firebase

class UserSettingsPage extends StatelessWidget {
  const UserSettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    // Use a base size similar to your design, e.g., 1600x900
    const double baseWidth = 1600;
    const double baseHeight = 900;
    return Scaffold(
      backgroundColor: const Color(0xFF191919),
      body: Stack(
        children: [
          Positioned.fill(
            child: Image.asset(
              'assets/images/Background.png',
              fit: BoxFit.cover,
            ),
          ),
          Center(
            child: FittedBox(
              fit: BoxFit.contain,
              child: SizedBox(
                width: baseWidth,
                height: baseHeight,
                child: SafeArea(
                  child: Stack(
                    children: [
                      Center(
                        child: SingleChildScrollView(
                          child: Container(
                            width: baseWidth * 0.95,
                            padding: const EdgeInsets.all(32),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.center,
                              children: [
                                // Top navigation with back button and separator
                                Column(
                                  children: [
                                    Row(
                                      children: [
                                        IconButton(
                                          icon: const Icon(
                                            Icons.arrow_back_ios,
                                            color: Colors.white,
                                            size: 28,
                                          ),
                                          onPressed: () {
                                            Navigator.of(context).maybePop();
                                          },
                                          padding: const EdgeInsets.only(
                                            right: 24,
                                          ),
                                        ),
                                        Expanded(
                                          child: Row(
                                            mainAxisAlignment:
                                                MainAxisAlignment.center,
                                            children: [
                                              _TabButton(
                                                label: 'APP SETTINGS',
                                                selected: false,
                                              ),
                                              const SizedBox(width: 32),
                                              _TabButton(
                                                label: 'USER SETTINGS',
                                                selected: true,
                                              ),
                                              const SizedBox(width: 32),
                                              _TabButton(
                                                label: 'ROBOT SETTINGS',
                                                selected: false,
                                              ),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 8),
                                    Container(
                                      width: double.infinity,
                                      height: 2,
                                      color: Colors.white,
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 32),
                                Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    // Profile Settings
                                    Expanded(
                                      flex: 2,
                                      child: _ProfileSettings(),
                                    ),
                                    const SizedBox(width: 32),
                                    // Account Settings
                                    Expanded(
                                      flex: 3,
                                      child: _AccountSettingsRefined(),
                                    ),
                                    const SizedBox(width: 32),
                                    // Linked Accounts
                                    Expanded(flex: 2, child: _LinkedAccounts()),
                                  ],
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
            ),
          ),
        ],
      ),
    );
  }
}

class _TabButton extends StatelessWidget {
  final String label;
  final bool selected;
  const _TabButton({required this.label, required this.selected});
  @override
  Widget build(BuildContext context) {
    return Text(
      label.toLowerCase(),
      style: TextStyle(
        fontFamily: 'Hyperion',
        fontWeight: FontWeight.bold,
        fontSize: 20,
        color: selected ? Colors.white : Colors.white54,
        letterSpacing: 2,
      ),
    );
  }
}

class _ProfileSettings extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF232323),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'profile picture',
            style: TextStyle(
              fontFamily: 'Hyperion',
              fontWeight: FontWeight.bold,
              fontSize: 18,
              color: Colors.white,
              letterSpacing: 1.5,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.asset(
                  'assets/images/Robot - Inverted 1.png',
                  width: 80,
                  height: 80,
                  fit: BoxFit.cover,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'uploaded image: your.jpg',
                      style: TextStyle(
                        fontFamily: 'Hyperion',
                        color: Colors.white,
                        fontSize: 12,
                      ),
                    ),
                    Text(
                      'supported file types are: jpg, jpeg, png.',
                      style: TextStyle(
                        fontFamily: 'Hyperion',
                        color: Colors.white70,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Column(
                children: [
                  ElevatedButton.icon(
                    onPressed: () {},
                    icon: Image.asset(
                      'assets/images/Upload.png',
                      width: 18,
                      height: 18,
                    ),
                    label: const Text('change image'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF191919),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  ElevatedButton.icon(
                    onPressed: () {},
                    icon: Image.asset(
                      'assets/images/Clear Symbol.png',
                      width: 18,
                      height: 18,
                    ),
                    label: const Text('remove image'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF191919),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 24),
          Text(
            'profile settings',
            style: TextStyle(
              fontFamily: 'Hyperion',
              fontWeight: FontWeight.bold,
              fontSize: 18,
              color: Colors.white,
              letterSpacing: 1.5,
            ),
          ),
          const SizedBox(height: 16),
          _ProfileTextField(label: 'first name', initialValue: 'begad'),
          _ProfileTextField(label: 'last name', initialValue: 'tamim'),
          _ProfileTextField(label: 'nickname', initialValue: 'bego'),
          Row(
            children: [
              Checkbox(value: false, onChanged: (_) {}),
              Text(
                'just use my full name',
                style: TextStyle(
                  fontFamily: 'Hyperion',
                  fontWeight: FontWeight.w400,
                  color: Colors.white70,
                ),
              ),
            ],
          ),
          _ProfileTextField(label: 'title', initialValue: 'eng'),
          _ProfileTextField(label: 'gender', initialValue: 'male'),
          // Date of Birth with age and calendar icon
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 4.0),
            child: Row(
              children: [
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      color: const Color(0xFF191919),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.white24),
                    ),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 8,
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text(
                            '28/12/2003',
                            style: TextStyle(
                              fontFamily: 'Hyperion',
                              color: Colors.white,
                              fontSize: 16,
                            ),
                          ),
                        ),
                        Image.asset(
                          'assets/images/Calendar 28.png',
                          width: 24,
                          height: 24,
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  'this makes you\n21 yrs old',
                  textAlign: TextAlign.right,
                  style: TextStyle(
                    fontFamily: 'Hyperion',
                    color: Colors.white,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
          _ProfileTextField(
            label: 'occupation',
            initialValue: 'dog food tester',
          ),
          _ProfileTextField(label: 'bio', initialValue: ''),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () {},
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.white10,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
            child: const Text('save changes'),
          ),
        ],
      ),
    );
  }
}

class _ProfileTextField extends StatelessWidget {
  final String label;
  final String initialValue;
  const _ProfileTextField({required this.label, required this.initialValue});
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toLowerCase(),
            style: TextStyle(
              fontFamily: 'Hyperion',
              fontWeight: FontWeight.w400,
              color: Colors.white70,
              fontSize: 12,
            ),
          ),
          const SizedBox(height: 2),
          TextFormField(
            initialValue: initialValue,
            style: const TextStyle(
              fontFamily: 'Hyperion',
              fontWeight: FontWeight.w400,
              color: Colors.white,
            ),
            decoration: InputDecoration(
              filled: true,
              fillColor: const Color(0xFF191919),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide.none,
              ),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 8,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _AccountSettingsRefined extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF232323),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // EMAILS
          _EmailsBox(),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: const Color(0xFF191919),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.white24),
                  ),
                  child: TextFormField(
                    style: const TextStyle(
                      fontFamily: 'Hyperion',
                      color: Colors.white,
                    ),
                    decoration: InputDecoration(
                      hintText: 'add mail',
                      hintStyle: const TextStyle(
                        fontFamily: 'Hyperion',
                        color: Colors.white54,
                      ),
                      border: InputBorder.none,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 16,
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              SizedBox(
                height: 48,
                child: ElevatedButton(
                  onPressed: () {},
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    padding: const EdgeInsets.symmetric(horizontal: 28),
                  ),
                  child: const Text(
                    'add mail',
                    style: TextStyle(
                      fontFamily: 'Hyperion',
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          // CHANGE PASSWORD
          Text(
            'change password',
            style: TextStyle(
              fontFamily: 'Hyperion',
              fontWeight: FontWeight.bold,
              color: Colors.white,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 8),
          _PasswordField(label: 'current password'),
          _PasswordField(label: 'new password'),
          _PasswordField(label: 'repeat password'),
          Row(
            children: [
              const Icon(Icons.error, color: Colors.red, size: 18),
              const SizedBox(width: 8),
              Text(
                'wrong current password',
                style: TextStyle(
                  fontFamily: 'Hyperion',
                  color: Colors.red,
                  fontSize: 12,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              onPressed: () {},
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: Colors.black,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: const Text(
                'save',
                style: TextStyle(
                  fontFamily: 'Hyperion',
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          const SizedBox(height: 24),
          // CONTACT SUPPORT
          Text(
            'contact support',
            style: TextStyle(
              fontFamily: 'Hyperion',
              fontWeight: FontWeight.bold,
              color: Colors.white,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'have a question or need help with your account, your robot, or the app? feel free to reach out to us through any of the following methods:',
            style: TextStyle(
              fontFamily: 'Hyperion',
              color: Colors.white70,
              fontSize: 11,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: _SupportButton(
                  icon: 'assets/images/Letter.png',
                  label: 'email',
                  white: true,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _SupportButton(
                  icon: 'assets/images/WhatsApp.png',
                  label: 'whatsapp',
                  white: true,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _SupportButton(
                  icon: 'assets/images/Task.png',
                  label: 'fill a form',
                  white: true,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          // LOGOUT
          Text(
            'log out from your account',
            style: TextStyle(
              fontFamily: 'Hyperion',
              fontWeight: FontWeight.bold,
              color: Colors.white,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              onPressed: () {},
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: Colors.black,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: const Text(
                'logout',
                style: TextStyle(
                  fontFamily: 'Hyperion',
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          const SizedBox(height: 24),
          // CLOSE ACCOUNT
          Text(
            'close your account',
            style: TextStyle(
              fontFamily: 'Hyperion',
              fontWeight: FontWeight.bold,
              color: Colors.white,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '• ',
                    style: TextStyle(color: Colors.white, fontSize: 18),
                  ),
                  Expanded(
                    child: Text(
                      'do you want to close your b.e.m.o account? we are sorry to see you go! please consider contacting support to let us know what went wrong.',
                      style: TextStyle(
                        fontFamily: 'Hyperion',
                        color: Colors.white70,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '• ',
                    style: TextStyle(color: Colors.white, fontSize: 18),
                  ),
                  Expanded(
                    child: Text(
                      'ready to move on? you can close your account—your data will be permanently deleted from our system after 30 days of inactivity.',
                      style: TextStyle(
                        fontFamily: 'Hyperion',
                        color: Colors.white70,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red[900],
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              onPressed: () {},
              child: const Text(
                'close account',
                style: TextStyle(
                  fontFamily: 'Hyperion',
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PasswordField extends StatefulWidget {
  final String label;
  const _PasswordField({required this.label});
  @override
  State<_PasswordField> createState() => _PasswordFieldState();
}

class _PasswordFieldState extends State<_PasswordField> {
  bool _obscure = true;
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Container(
        decoration: BoxDecoration(
          color: const Color(0xFF191919),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.white24),
        ),
        child: Row(
          children: [
            Expanded(
              child: TextFormField(
                obscureText: _obscure,
                style: const TextStyle(
                  fontFamily: 'Hyperion',
                  color: Colors.white,
                ),
                decoration: InputDecoration(
                  labelText: widget.label,
                  labelStyle: const TextStyle(
                    fontFamily: 'Hyperion',
                    color: Colors.white70,
                    fontSize: 12,
                  ),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 16,
                  ),
                ),
              ),
            ),
            IconButton(
              icon: Icon(
                _obscure ? Icons.visibility_off : Icons.visibility,
                color: Colors.white54,
              ),
              onPressed: () {
                setState(() {
                  _obscure = !_obscure;
                });
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _SupportButton extends StatelessWidget {
  final String icon;
  final String label;
  final bool white;
  const _SupportButton({
    required this.icon,
    required this.label,
    this.white = false,
  });
  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      onPressed: () {},
      icon: Image.asset(icon, width: 22, height: 22),
      label: Text(
        label.toLowerCase(),
        style: TextStyle(
          fontFamily: 'Hyperion',
          color: white ? Colors.black : Colors.white,
          fontWeight: FontWeight.bold,
        ),
      ),
      style: ElevatedButton.styleFrom(
        backgroundColor: white ? Colors.white : const Color(0xFF191919),
        foregroundColor: white ? Colors.black : Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 16),
      ),
    );
  }
}

class _EmailsBox extends StatelessWidget {
  final List<String> emails = const [
    'begadtamim.a@gmail.com',
    'begadt@gmail.com',
    'momadoz003@hotmail.com',
    'notmomad00555555@gmail.com',
    'notmomad00555555@gmail.com',
  ];
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'emails',
          style: TextStyle(
            fontFamily: 'Hyperion',
            fontWeight: FontWeight.bold,
            color: Colors.white,
            fontSize: 14,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            color: Colors.black,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.white24),
          ),
          padding: const EdgeInsets.all(12),
          child: Column(
            children: emails
                .map(
                  (email) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 6.0),
                    child: Row(
                      children: [
                        const Text(
                          '• ',
                          style: TextStyle(color: Colors.white, fontSize: 18),
                        ),
                        Expanded(
                          child: Text(
                            email,
                            style: TextStyle(
                              fontFamily: 'Hyperion',
                              color: Colors.white,
                              fontSize: 13,
                            ),
                          ),
                        ),
                        Row(
                          children: [
                            Container(
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(4),
                                border: Border.all(color: Colors.white24),
                              ),
                              padding: const EdgeInsets.all(2),
                              child: Image.asset(
                                'assets/images/Connect.png',
                                width: 22,
                                height: 22,
                                color: Colors.black,
                              ),
                            ),
                            const SizedBox(width: 4),
                            Container(
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(4),
                                border: Border.all(color: Colors.white24),
                              ),
                              padding: const EdgeInsets.all(2),
                              child: Image.asset(
                                'assets/images/Task.png',
                                width: 22,
                                height: 22,
                              ),
                            ),
                            const SizedBox(width: 4),
                            Container(
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(4),
                                border: Border.all(color: Colors.white24),
                              ),
                              padding: const EdgeInsets.all(2),
                              child: Image.asset(
                                'assets/images/Crown.png',
                                width: 22,
                                height: 22,
                              ),
                            ),
                            const SizedBox(width: 4),
                            Container(
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(4),
                                border: Border.all(color: Colors.white24),
                              ),
                              padding: const EdgeInsets.all(2),
                              child: Image.asset(
                                'assets/images/Delete.png',
                                width: 22,
                                height: 22,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                )
                .toList(),
          ),
        ),
        const SizedBox(height: 4),
        GestureDetector(
          onTap: () {},
          child: Text.rich(
            TextSpan(
              children: [
                TextSpan(
                  text: 'click here',
                  style: TextStyle(
                    fontFamily: 'Hyperion',
                    color: Colors.white,
                    decoration: TextDecoration.underline,
                  ),
                ),
                TextSpan(
                  text: ' for more information about email settings',
                  style: TextStyle(
                    fontFamily: 'Hyperion',
                    color: Colors.white70,
                  ),
                ),
              ],
            ),
            style: const TextStyle(fontSize: 11),
          ),
        ),
      ],
    );
  }
}

class _LinkedAccounts extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF232323),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'linked accounts',
            style: TextStyle(
              fontFamily: 'Hyperion',
              fontWeight: FontWeight.bold,
              fontSize: 18,
              color: Colors.white,
              letterSpacing: 1.5,
            ),
          ),
          const SizedBox(height: 16),
          _LinkedAccountButton(
            icon: 'assets/images/Google.png',
            label: 'disconnect google',
            connected: true,
            color: Colors.red,
          ),
          _LinkedAccountButton(
            icon: 'assets/images/Microsoft.png',
            label: 'disconnect microsoft',
            connected: true,
            color: Colors.red,
          ),
          _LinkedAccountButton(
            icon: 'assets/images/Apple Inc.png',
            label: 'connect to apple',
            connected: false,
            color: Colors.green,
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF191919),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              'google: used for quick login, mailassist, and taskflow\nmicrosoft: used for quick login, and mailassist\napple: used for quick login only\n\ndisconnecting will remove all related data from B.E.M.O. but you may still need to revoke access on the linked service.\nconnected accounts are also listed under emails in account settings.',
              style: TextStyle(
                fontFamily: 'Hyperion',
                color: Colors.white70,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _LinkedAccountButton extends StatelessWidget {
  final String icon;
  final String label;
  final bool connected;
  final Color color;
  const _LinkedAccountButton({
    required this.icon,
    required this.label,
    required this.connected,
    required this.color,
  });
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: SizedBox(
        width: double.infinity,
        height: 48,
        child: ElevatedButton.icon(
          onPressed: () {},
          icon: Image.asset(icon, width: 24, height: 24),
          label: Text(
            label.toLowerCase(),
            style: TextStyle(
              fontFamily: 'Hyperion',
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          style: ElevatedButton.styleFrom(
            backgroundColor: color,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
      ),
    );
  }
}
