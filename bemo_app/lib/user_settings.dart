import 'package:flutter/material.dart';

class UserSettingsPage extends StatelessWidget {
  const UserSettingsPage({Key? key}) : super(key: key);

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
              'assets/Images/Background.png',
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
                                          icon: const Icon(Icons.arrow_back_ios, color: Colors.white, size: 28),
                                          onPressed: () {
                                            Navigator.of(context).maybePop();
                                          },
                                          padding: const EdgeInsets.only(right: 24),
                                        ),
                                        Expanded(
                                          child: Row(
                                            mainAxisAlignment: MainAxisAlignment.center,
                                            children: [
                                              _TabButton(label: 'APP SETTINGS', selected: false),
                                              const SizedBox(width: 32),
                                              _TabButton(label: 'USER SETTINGS', selected: true),
                                              const SizedBox(width: 32),
                                              _TabButton(label: 'ROBOT SETTINGS', selected: false),
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
                                    Expanded(
                                      flex: 2,
                                      child: _LinkedAccounts(),
                                    ),
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
      label,
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
          Text('PROFILE PICTURE',
              style: TextStyle(
                fontFamily: 'Hyperion',
                fontWeight: FontWeight.bold,
                fontSize: 18,
                color: Colors.white,
                letterSpacing: 1.5,
              )),
          const SizedBox(height: 8),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.asset(
                  'assets/Images/Robot - Inverted 1.png',
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
                    Text('UPLOADED IMAGE: YOUR.JPG',
                        style: TextStyle(
                          fontFamily: 'Hyperion',
                          color: Colors.white,
                          fontSize: 12,
                        )),
                    Text('SUPPORTED FILE TYPES ARE: JPG, JPEG, PNG.',
                        style: TextStyle(
                          fontFamily: 'Hyperion',
                          color: Colors.white70,
                          fontSize: 12,
                        )),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Column(
                children: [
                  ElevatedButton.icon(
                    onPressed: () {},
                    icon: Image.asset('assets/Images/Upload.png', width: 18, height: 18),
                    label: const Text('CHANGE IMAGE'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF191919),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  ElevatedButton.icon(
                    onPressed: () {},
                    icon: Image.asset('assets/Images/Clear Symbol.png', width: 18, height: 18),
                    label: const Text('REMOVE IMAGE'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF191919),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
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
          Text('PROFILE SETTINGS',
              style: TextStyle(
                fontFamily: 'Hyperion',
                fontWeight: FontWeight.bold,
                fontSize: 18,
                color: Colors.white,
                letterSpacing: 1.5,
              )),
          const SizedBox(height: 16),
          _ProfileTextField(label: 'FIRST NAME', initialValue: 'BEGAD'),
          _ProfileTextField(label: 'LAST NAME', initialValue: 'TAMIM'),
          _ProfileTextField(label: 'NICKNAME', initialValue: 'BEGO'),
          Row(
            children: [
              Checkbox(value: false, onChanged: (_) {}),
              const Text('JUST USE MY FULL NAME',
                  style: TextStyle(
                    fontFamily: 'Hyperion',
                    fontWeight: FontWeight.w400,
                    color: Colors.white70,
                  )),
            ],
          ),
          _ProfileTextField(label: 'TITLE', initialValue: 'ENG'),
          _ProfileTextField(label: 'GENDER', initialValue: 'MALE'),
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
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text('28/12/2003',
                            style: TextStyle(
                              fontFamily: 'Hyperion',
                              color: Colors.white,
                              fontSize: 16,
                            ),
                          ),
                        ),
                        Image.asset('assets/Images/Calendar 28.png', width: 24, height: 24),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Text('THIS MAKES YOU\n21 YRS OLD',
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
          _ProfileTextField(label: 'OCCUPATION', initialValue: 'DOG FOOD TESTER'),
          _ProfileTextField(label: 'BIO', initialValue: ''),
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
            child: const Text('SAVE CHANGES TO PROFILE SETTINGS'),
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
          Text(label,
              style: TextStyle(
                fontFamily: 'Hyperion',
                fontWeight: FontWeight.w400,
                color: Colors.white70,
                fontSize: 12,
              )),
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
              contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
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
                      hintText: 'ADD MAIL',
                      hintStyle: const TextStyle(
                        fontFamily: 'Hyperion',
                        color: Colors.white54,
                      ),
                      border: InputBorder.none,
                      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
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
                  child: const Text('ADD MAIL', style: TextStyle(fontFamily: 'Hyperion', fontWeight: FontWeight.bold)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          // CHANGE PASSWORD
          Text('CHANGE PASSWORD',
              style: TextStyle(
                fontFamily: 'Hyperion',
                fontWeight: FontWeight.bold,
                color: Colors.white,
                fontSize: 14,
              )),
          const SizedBox(height: 8),
          _PasswordField(label: 'CURRENT PASSWORD'),
          _PasswordField(label: 'NEW PASSWORD'),
          _PasswordField(label: 'REPEAT PASSWORD'),
          Row(
            children: [
              const Icon(Icons.error, color: Colors.red, size: 18),
              const SizedBox(width: 8),
              Text('WRONG CURRENT PASSWORD',
                  style: TextStyle(
                    fontFamily: 'Hyperion',
                    color: Colors.red,
                    fontSize: 12,
                  )),
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
              child: const Text('SAVE', style: TextStyle(fontFamily: 'Hyperion', fontWeight: FontWeight.bold)),
            ),
          ),
          const SizedBox(height: 24),
          // CONTACT SUPPORT
          Text('CONTACT SUPPORT',
              style: TextStyle(
                fontFamily: 'Hyperion',
                fontWeight: FontWeight.bold,
                color: Colors.white,
                fontSize: 14,
              )),
          const SizedBox(height: 4),
          Text(
            'HAVE A QUESTION OR NEED HELP WITH YOUR ACCOUNT, YOUR ROBOT, OR THE APP? FEEL FREE TO REACH OUT TO US THROUGH ANY OF THE FOLLOWING METHODS:',
            style: TextStyle(
              fontFamily: 'Hyperion',
              color: Colors.white70,
              fontSize: 11,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(child: _SupportButton(icon: 'assets/Images/Letter.png', label: 'EMAIL', white: true)),
              const SizedBox(width: 8),
              Expanded(child: _SupportButton(icon: 'assets/Images/WhatsApp.png', label: 'WHATSAPP', white: true)),
              const SizedBox(width: 8),
              Expanded(child: _SupportButton(icon: 'assets/Images/Task.png', label: 'FILL A FORM', white: true)),
            ],
          ),
          const SizedBox(height: 24),
          // LOGOUT
          Text('LOG OUT FROM YOUR ACCOUNT',
              style: TextStyle(
                fontFamily: 'Hyperion',
                fontWeight: FontWeight.bold,
                color: Colors.white,
                fontSize: 14,
              )),
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
              child: const Text('LOGOUT', style: TextStyle(fontFamily: 'Hyperion', fontWeight: FontWeight.bold)),
            ),
          ),
          const SizedBox(height: 24),
          // CLOSE ACCOUNT
          Text('CLOSE YOUR ACCOUNT',
              style: TextStyle(
                fontFamily: 'Hyperion',
                fontWeight: FontWeight.bold,
                color: Colors.white,
                fontSize: 14,
              )),
          const SizedBox(height: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('• ', style: TextStyle(color: Colors.white, fontSize: 18)),
                  Expanded(
                    child: Text(
                      'DO YOU WANT TO CLOSE YOUR B.E.M.O ACCOUNT? WE ARE SORRY TO SEE YOU GO! PLEASE CONSIDER CONTACTING SUPPORT TO LET US KNOW WHAT WENT WRONG.',
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
                  const Text('• ', style: TextStyle(color: Colors.white, fontSize: 18)),
                  Expanded(
                    child: Text(
                      'READY TO MOVE ON? YOU CAN CLOSE YOUR ACCOUNT—YOUR DATA WILL BE PERMANENTLY DELETED FROM OUR SYSTEM AFTER 30 DAYS OF INACTIVITY.',
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
              child: const Text('CLOSE ACCOUNT', style: TextStyle(fontFamily: 'Hyperion', fontWeight: FontWeight.bold)),
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
                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
                ),
              ),
            ),
            IconButton(
              icon: Icon(_obscure ? Icons.visibility_off : Icons.visibility, color: Colors.white54),
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
  const _SupportButton({required this.icon, required this.label, this.white = false});
  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      onPressed: () {},
      icon: Image.asset(icon, width: 22, height: 22),
      label: Text(label,
        style: TextStyle(
          fontFamily: 'Hyperion',
          color: white ? Colors.black : Colors.white,
          fontWeight: FontWeight.bold,
        ),
      ),
      style: ElevatedButton.styleFrom(
        backgroundColor: white ? Colors.white : const Color(0xFF191919),
        foregroundColor: white ? Colors.black : Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 16),
      ),
    );
  }
}

class _EmailsBox extends StatelessWidget {
  final List<String> emails = const [
    'BEGADTAMIM.A@GMAIL.COM',
    'BEGADT@GMAIL.COM',
    'MOMADOZ003@HOTMAIL.COM',
    'NOTMOMAD00555555@GMAIL.COM',
    'NOTMOMAD00555555@GMAIL.COM',
  ];
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('EMAILS',
            style: TextStyle(
              fontFamily: 'Hyperion',
              fontWeight: FontWeight.bold,
              color: Colors.white,
              fontSize: 14,
            )),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            color: Colors.black,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.white24),
          ),
          padding: const EdgeInsets.all(12),
          child: Column(
            children: emails.map((email) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 6.0),
              child: Row(
                children: [
                  const Text('• ', style: TextStyle(color: Colors.white, fontSize: 18)),
                  Expanded(
                    child: Text(email,
                      style: TextStyle(
                        fontFamily: 'Hyperion',
                        color: Colors.white,
                        fontSize: 13,
                      ),
                    ),
                  ),
                  Row(
                    children: [
                      Image.asset('assets/Images/Connect.png', width: 22, height: 22),
                      const SizedBox(width: 4),
                      Image.asset('assets/Images/Task.png', width: 22, height: 22),
                      const SizedBox(width: 4),
                      Image.asset('assets/Images/Crown.png', width: 22, height: 22),
                      const SizedBox(width: 4),
                      Image.asset('assets/Images/Delete.png', width: 22, height: 22),
                    ],
                  ),
                ],
              ),
            )).toList(),
          ),
        ),
        const SizedBox(height: 4),
        GestureDetector(
          onTap: () {},
          child: Text.rich(
            TextSpan(
              children: [
                TextSpan(
                  text: 'CLICK HERE',
                  style: TextStyle(
                    fontFamily: 'Hyperion',
                    color: Colors.white,
                    decoration: TextDecoration.underline,
                  ),
                ),
                TextSpan(
                  text: ' FOR MORE INFORMATION ABOUT EMAIL SETTINGS',
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
          Text('LINKED ACCOUNTS',
              style: TextStyle(
                fontFamily: 'Hyperion',
                fontWeight: FontWeight.bold,
                fontSize: 18,
                color: Colors.white,
                letterSpacing: 1.5,
              )),
          const SizedBox(height: 16),
          _LinkedAccountButton(
            icon: 'assets/Images/Google.png',
            label: 'DISCONNECT GOOGLE',
            connected: true,
            color: Colors.red,
          ),
          _LinkedAccountButton(
            icon: 'assets/Images/Microsoft.png',
            label: 'DISCONNECT MICROSOFT',
            connected: true,
            color: Colors.red,
          ),
          _LinkedAccountButton(
            icon: 'assets/Images/Apple Inc.png',
            label: 'CONNECT TO APPLE',
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
              'GOOGLE: used for quick login, mailassist, and taskflow\nMICROSOFT: used for quick login, and mailassist\nAPPLE: used for quick login only\n\nDisconnecting will remove all related data from B.E.M.O. but you may still need to revoke access on the linked service.\nConnected accounts are also listed under emails in account settings.',
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
  const _LinkedAccountButton({required this.icon, required this.label, required this.connected, required this.color});
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
          label: Text(label,
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