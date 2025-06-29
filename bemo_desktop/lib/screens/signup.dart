import '../widgets/fields.dart';
import 'package:flutter/material.dart';
import '../services/firebase_user_service.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _formKey = GlobalKey<FormState>();
  final FirebaseUserService _auth = FirebaseUserService();

  bool _obscurePassword = true;
  bool darkMode = true;
  bool submitted = false;

  // Firebase error
  String? firebaseError;

  // Controllers
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  final repeatPasswordController = TextEditingController();

  @override
  void dispose() {
    emailController.dispose();
    passwordController.dispose();
    repeatPasswordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Background image
          SizedBox.expand(
            child: Image.asset(
              'assets/images/signup_login_background.png',
              fit: BoxFit.cover,
            ),
          ),

          // Signup form
          Center(
            child: Container(
              height: 600,
              width: 500,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: darkMode ? Color(0xFF191919) : Color(0xFFEFEFEF),
                borderRadius: BorderRadius.circular(24),
              ),
              child: Form(
                key: _formKey,
                autovalidateMode: submitted
                    ? AutovalidateMode.onUserInteraction
                    : AutovalidateMode.disabled,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'join the bemo club',
                      style: TextStyle(
                        fontFamily: 'Hyperion',
                        fontSize: 28,
                        color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    Text(
                      "we promise we won't sell your data",
                      style: TextStyle(
                        fontFamily: 'Hyperion',
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: darkMode ? Color(0xB0EFEFEF) : Color(0xFF191919),
                      ),
                    ),

                    const SizedBox(height: 12),

                    // Firebase error message
                    if (firebaseError != null)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: Text(
                          firebaseError!,
                          style: const TextStyle(
                            fontFamily: 'Hyperion',
                            fontWeight: FontWeight.w700,
                            fontSize: 14,
                            color: Colors.red,
                          ),
                        ),
                      ),

                    // Email Field
                    buildField(
                      darkMode,
                      'email address',
                      controller: emailController,
                      hintText: 'cringyusername@example.com',
                      labelNote: '(required)',
                      required: true,
                    ),
                    const SizedBox(height: 12),

                    // Password Field
                    buildPasswordField(
                      darkMode,
                      'password',
                      controller: passwordController,
                      labelNote: '(required)',
                      obscureText: _obscurePassword,
                      toggle: () => setState(() {
                        _obscurePassword = !_obscurePassword;
                      }),
                    ),
                    const SizedBox(height: 12),

                    // Repeat Password Field
                    buildPasswordField(
                      darkMode,
                      'repeat password',
                      controller: repeatPasswordController,
                      labelNote: '(just ctrl+c ctrl+v man)',
                      obscureText: _obscurePassword,
                      toggle: () => setState(() {
                        _obscurePassword = !_obscurePassword;
                      }),
                    ),
                    const SizedBox(height: 18),

                    // Sign Up Button
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: darkMode
                              ? Color(0xFFEFEFEF)
                              : Color(0xFF191919),
                          foregroundColor: darkMode
                              ? Colors.black
                              : Color(0xFFEFEFEF),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        // onPressed: _signUp,
                        onPressed: () async {
                          setState(() {
                            submitted = true;
                          });

                          if (_formKey.currentState!.validate()) {
                            if (passwordController.text.trim() !=
                                repeatPasswordController.text.trim()) {
                              showDialog(
                                context: context,
                                builder: (_) => AlertDialog(
                                  title: Text("Signup Failed"),
                                  content: Text("Passwords do not match"),
                                ),
                              );
                              return;
                            }

                            final result = await _auth.signUp(
                              emailController.text.trim(),
                              passwordController.text.trim(),
                            );

                            if (result.containsKey('error')) {
                              showDialog(
                                context: context,
                                builder: (_) => AlertDialog(
                                  title: Text("Signup Failed"),
                                  content: Text(result['error']['message']),
                                ),
                              );
                            } else {
                              final String uid = result['localId'];
                              final String idToken = result['idToken'];

                              Navigator.pushNamed(
                                context,
                                '/getting-started',
                                arguments: {
                                  'uid': uid,
                                  'idToken': idToken,
                                  'email': emailController.text
                                      .trim(), //Todo: Remove this and implement firebase user service function to fetch user data
                                },
                              );
                            }
                          }
                        },

                        child: Text(
                          'sign up',
                          style: TextStyle(
                            fontFamily: 'Hyperion',
                            fontSize: 22,
                            fontWeight: FontWeight.w700,
                            color: darkMode
                                ? Color(0xFF191919)
                                : Color(0xFFEFEFEF),
                          ),
                        ),
                      ),
                    ),

                    const SizedBox(height: 12),

                    // Divider with text
                    Row(
                      children: [
                        Expanded(
                          child: Divider(
                            color: darkMode
                                ? Color(0xB3EFEFEF)
                                : Color(0xFF191919),
                            thickness: 1,
                            endIndent: 12,
                          ),
                        ),
                        Text(
                          'or the easier option',
                          style: TextStyle(
                            fontFamily: 'Hyperion',
                            fontWeight: FontWeight.w700,
                            fontSize: 15,
                            color: darkMode
                                ? Color(0xB3EFEFEF)
                                : Color(0xB3101010),
                          ),
                        ),
                        Expanded(
                          child: Divider(
                            color: darkMode
                                ? Color(0xB3EFEFEF)
                                : Color(0xB3101010),
                            thickness: 1,
                            indent: 12,
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 10),

                    // Social Buttons
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        buildIconButton(
                          darkMode,
                          'assets/images/Google.png',
                          onPressed: () async {
                            // final result = await _auth.signUpWithGoogle();
                            // print('result: $result');
                            // Navigator.pushNamed(
                            //   context,
                            //   '/getting-started',
                            //   arguments: {
                            //     'uid': result['localId'],
                            //     'idToken': result['idToken'],
                            //     'email': result['email'],
                            //   },
                            // );
                          },
                        ),
                        const SizedBox(width: 16),
                        buildIconButton(darkMode, 'assets/images/Apple.png'),
                        const SizedBox(width: 16),
                        buildIconButton(
                          darkMode,
                          'assets/images/Microsoft.png',
                        ),
                      ],
                    ),

                    const SizedBox(height: 8),

                    // Login Link
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          "already a part of the cool club?",
                          style: TextStyle(
                            fontFamily: 'Hyperion',
                            fontWeight: FontWeight.w700,
                            fontSize: 13,
                            color: darkMode
                                ? Color(0xD9EFEFEF)
                                : Color(0xFF101010),
                          ),
                        ),
                        TextButton(
                          onPressed: () {
                            Navigator.pushNamed(context, '/login');
                          },
                          child: Text(
                            'login',
                            style: TextStyle(
                              decoration: TextDecoration.underline,
                              decorationColor: darkMode
                                  ? Color(0xFFEFEFEF)
                                  : Color(0xFF191919),
                              fontFamily: 'Hyperion',
                              fontWeight: FontWeight.w700,
                              fontSize: 13,
                              color: darkMode
                                  ? Color(0xFFEFEFEF)
                                  : Color(0xFF101010),
                            ),
                          ),
                        ),
                      ],
                    ),

                    // Terms
                    TextButton(
                      onPressed: () {},
                      child: Text(
                        'terms and conditions',
                        style: TextStyle(
                          fontFamily: 'Hyperion',
                          fontWeight: FontWeight.w700,
                          fontSize: 10,
                          decoration: TextDecoration.underline,
                          decorationColor: darkMode
                              ? Color(0xFFEFEFEF)
                              : Color(0xFF191919),
                          color: darkMode
                              ? Color(0xFFEFEFEF)
                              : Color(0xFF191919),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
