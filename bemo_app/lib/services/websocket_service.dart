import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;

class WebSocketService {
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;
  WebSocketService._internal();

  static const String robotId = 'user-MK1';
  static const String serverUrl = 'wss://b-e-m-o.onrender.com/api/ws/';
  WebSocketChannel? _channel;
  StreamController<Map<String, dynamic>> _messageController =
      StreamController.broadcast();
  Stream<Map<String, dynamic>> get messages => _messageController.stream;

  // Global chat messages that persist across pages
  final List<Map<String, dynamic>> _chatMessages = [];
  List<Map<String, dynamic>> get chatMessages =>
      List.unmodifiable(_chatMessages);

  bool _connected = false;
  int _retryCount = 0;
  final int _maxRetries = 3;
  final Duration _retryInterval = Duration(seconds: 10);

  // Getter for connection status
  bool get isConnected => _connected;

  // Method to add message to global chat
  void addChatMessage(Map<String, dynamic> message) {
    _chatMessages.add(message);
    print(
        'Message added to global chat. Total messages: ${_chatMessages.length}');
  }

  // Method to clear chat messages
  void clearChatMessages() {
    _chatMessages.clear();
    print('Chat messages cleared');
  }

  void _addMessageToGlobalChat(Map<String, dynamic> msg) {
    // Handle server error notification
    if (msg['is_server_error'] == true && msg['error'] != null) {
      _chatMessages.add({
        'fromUser': false,
        'text': msg['error'],
        'time': DateTime.now().toString(),
        'method': null,
        'is_server_error': true,
      });
      return;
    }

    // Add user prompt
    if (msg['prompt'] != null) {
      _chatMessages.add({
        'fromUser': true,
        'text': msg['prompt'],
        'time': DateTime.now().toString(),
      });
    }

    // Add robot response
    if (msg['response'] != null) {
      _chatMessages.add({
        'fromUser': false,
        'text': msg['response'],
        'time': DateTime.now().toString(),
        'method':
            msg['task_results'] != null ? msg['task_results']['method'] : null,
      });
    }

    // Add generic bot message
    if (msg['message'] != null) {
      _chatMessages.add({
        'fromUser': false,
        'text': msg['message'],
        'time': DateTime.now().toString(),
        'method': null,
      });
    }

    print(
        'Message added to global chat. Total messages: ${_chatMessages.length}');
  }

  void connect() {
    print('Attempting to connect to WebSocket...');
    final url = serverUrl + robotId;
    print('Connecting to: $url');

    try {
      _channel = WebSocketChannel.connect(Uri.parse(url));
      _connected = true;
      _retryCount = 0;
      print('WebSocket connected successfully!');

      _channel!.stream.listen(
        (message) {
          try {
            final decoded = json.decode(message);
            if (decoded is Map<String, dynamic>) {
              _messageController.add(decoded);

              // Add to global chat messages
              _addMessageToGlobalChat(decoded);
            }
          } catch (e) {
            print('Error parsing message: $e');
          }
        },
        onError: (error) {
          _connected = false;
          print('WebSocket error: $error');
          _handleError(error);
        },
        onDone: () {
          _connected = false;
          print('WebSocket connection closed');
          _handleClose();
        },
        cancelOnError: true,
      );
    } catch (e) {
      _connected = false;
      print('Failed to establish WebSocket connection: $e');
      _handleError(e);
    }
  }

  void _handleError(error) {
    print('WebSocket error: $error');
    _tryReconnect();
  }

  void _handleClose() {
    print('WebSocket connection closed');
    _tryReconnect();
  }

  void _tryReconnect() {
    if (_retryCount < _maxRetries) {
      _retryCount++;
      print('Attempting to reconnect ($_retryCount/$_maxRetries)...');
      Future.delayed(_retryInterval, connect);
    } else {
      print('Max retries reached. Connection failed permanently.');
    }
  }

  void send(dynamic data) {
    if (data is Map<String, dynamic> && !data.containsKey('src_user_id')) {
      data['src_user_id'] = 'user-MK1';
    }
    if (_connected && _channel != null) {
      _channel!.sink.add(json.encode(data));
      print('Message sent: ${json.encode(data)}');
    } else {
      print('WebSocket not connected. Cannot send message.');
    }
  }

  void disconnect() {
    print('Disconnecting WebSocket...');
    _channel?.sink.close(status.goingAway);
    _connected = false;
    print('WebSocket disconnected');
  }

  void dispose() {
    disconnect();
    _messageController.close();
  }
}
