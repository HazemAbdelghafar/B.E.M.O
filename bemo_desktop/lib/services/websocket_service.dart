import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;

class WebSocketService {
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;
  WebSocketService._internal();

  static const String robotId =
      'user-MK2'; //Todo: Change this to the user's robot id (user-MK1)
  static const String serverUrl = 'wss://b-e-m-o.onrender.com/api/ws/';
  WebSocketChannel? _channel;
  final StreamController<Map<String, dynamic>> _messageController =
      StreamController.broadcast();
  Stream<Map<String, dynamic>> get messages => _messageController.stream;

  bool _connected = false;
  int _retryCount = 0;
  final int _maxRetries = 3;
  final Duration _retryInterval = Duration(seconds: 10);

  void connect() {
    final url = serverUrl + robotId;
    _channel = WebSocketChannel.connect(Uri.parse(url));
    _connected = true;
    _retryCount = 0;
    _channel!.stream.listen(
      (message) {
        try {
          final decoded = json.decode(message);
          if (decoded is Map<String, dynamic>) {
            _messageController.add(decoded);
          }
        } catch (e) {
          // fallback: try literal eval style parsing if needed
          // (not typical in Dart)
        }
      },
      onError: (error) {
        _connected = false;
        _handleError(error);
      },
      onDone: () {
        _connected = false;
        _handleClose();
      },
      cancelOnError: true,
    );
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
    } else {
      print('WebSocket not connected.');
    }
  }

  void disconnect() {
    _channel?.sink.close(status.goingAway);
    _connected = false;
  }

  void dispose() {
    disconnect();
    _messageController.close();
  }
}
