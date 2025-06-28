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

  // Streaming related variables
  bool _isStreaming = false;
  Timer? _streamingTimer;
  int _currentStreamingIndex = 0;
  String _currentStreamingText = '';
  Map<String, dynamic>? _currentStreamingMessage;

  bool _connected = false;
  bool _connectionStable = false;  // New flag for stable connection
  Timer? _connectionStabilityTimer;  // Timer to check connection stability
  int _retryCount = 0;
  final int _maxRetries = 3;
  final Duration _retryInterval = Duration(seconds: 10);
  final Duration _connectionStabilityDelay = Duration(seconds: 3);  // Minimum time to consider connection stable

  // Getter for connection status
  bool get isConnected => _connectionStable;
  
  // Getter for streaming status
  bool get isStreaming => _isStreaming;

  // Method to add message to global chat
  void addChatMessage(Map<String, dynamic> message) {
    _chatMessages.add(message);
    print(
        'Message added to global chat. Total messages: ${_chatMessages.length}');
    // Notify listeners that messages have been updated
    _messageController.add({'type': 'messages_updated'});
  }

  // Method to clear chat messages
  void clearChatMessages() {
    _chatMessages.clear();
    print('Chat messages cleared');
    // Notify listeners that messages have been updated
    _messageController.add({'type': 'messages_updated'});
  }

  // Method to add test message for debugging
  void addTestMessage(String text, {bool isUser = false, bool isError = false}) {
    _chatMessages.add({
      'fromUser': isUser,
      'text': text,
      'time': DateTime.now().toString(),
      'method': null,
      'is_server_error': isError,
    });
    print('Test message added: "$text"');
    // Notify listeners that messages have been updated
    _messageController.add({'type': 'messages_updated'});
  }

  void _addMessageToGlobalChat(Map<String, dynamic> msg) {
    // Handle server error notification - but filter out connection-related errors
    if (msg['is_server_error'] == true && msg['error'] != null) {
      final errorText = msg['error'].toString().trim();
      if (errorText.isNotEmpty) {
        // Filter out connection-related error messages
        final lowerError = errorText.toLowerCase();
        if (!lowerError.contains('not connected') &&
            !lowerError.contains('connection') &&
            !lowerError.contains('server is not') &&
            !lowerError.contains('disconnected') &&
            !lowerError.contains('connection failed') &&
            !lowerError.contains('connection error')) {
          
          _chatMessages.add({
            'fromUser': false,
            'text': errorText,
            'time': DateTime.now().toString(),
            'method': null,
            'is_server_error': true,
          });
        } else {
          print('Filtering out connection-related error: "$errorText"');
        }
      }
      return;
    }

    // Add user prompt - only if not empty
    if (msg['prompt'] != null) {
      final promptText = msg['prompt'].toString().trim();
      if (promptText.isNotEmpty) {
        _chatMessages.add({
          'fromUser': true,
          'text': promptText,
          'time': DateTime.now().toString(),
        });
      }
    }

    // Add robot response - only if not empty and not an error
    if (msg['response'] != null) {
      final responseText = msg['response'].toString().trim();
      
      // Skip empty responses, null responses, or error indicators
      if (responseText.isNotEmpty && 
          responseText.toLowerCase() != 'null' &&
          responseText.toLowerCase() != 'undefined' &&
          responseText.toLowerCase() != 'error' &&
          !responseText.toLowerCase().contains('no response') &&
          !responseText.toLowerCase().contains('empty response')) {
        
        // Check if this is a learning resources response
        final taskResults = msg['task_results'];
        final isLearningResources = taskResults is Map &&
            taskResults['module_name'] == 'learning_resources' &&
            taskResults['resources'] is List;
        
        String finalResponseText = responseText;
        
        if (isLearningResources) {
          final resources = taskResults['resources'] as List;
          if (resources.isNotEmpty) {
            finalResponseText += '\n\n📚 Learning Resources:\n';
            for (final resource in resources) {
              if (resource is Map) {
                final title = resource['title']?.toString() ?? '';
                final url = resource['url']?.toString() ?? '';
                final type = resource['type']?.toString() ?? '';
                if (title.isNotEmpty && url.isNotEmpty) {
                  finalResponseText += '\n• $title';
                  if (type.isNotEmpty) {
                    finalResponseText += ' ($type)';
                  }
                  finalResponseText += '\n  $url';
                }
              }
            }
          }
        }
        
        // Print prompt and response for debugging
        print('Prompt: \'${msg['prompt'] ?? ''}\'');
        print('Response: $finalResponseText');
        
        // Add a 1 second delay before showing the bot response
        Future.delayed(const Duration(seconds: 1), () {
          _chatMessages.add({
            'fromUser': false,
            'text': finalResponseText,
            'time': DateTime.now().toString(),
            'method': taskResults is Map ? taskResults['module_name'] : null,
            'is_learning_resources': isLearningResources,
          });
          _messageController.add({'type': 'messages_updated'});
        });
      } else {
        print('Skipping empty or error response: "$responseText"');
      }
    }

    // Add generic bot message - only if not empty
    if (msg['message'] != null) {
      final messageText = msg['message'].toString().trim();
      if (messageText.isNotEmpty && 
          messageText.toLowerCase() != 'null' &&
          messageText.toLowerCase() != 'undefined' &&
          messageText.toLowerCase() != 'error' &&
          !messageText.toLowerCase().contains('no response') &&
          !messageText.toLowerCase().contains('empty response')) {
        
        _chatMessages.add({
          'fromUser': false,
          'text': messageText,
          'time': DateTime.now().toString(),
          'method': null,
        });
      } else {
        print('Skipping empty or error message: "$messageText"');
      }
    }

    print('Message processed. Total messages: ${_chatMessages.length}');
    
    // Notify listeners that messages have been updated
    _messageController.add({'type': 'messages_updated'});
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
      
      // Start connection stability timer
      _connectionStabilityTimer?.cancel();
      _connectionStabilityTimer = Timer(_connectionStabilityDelay, () {
        if (_connected) {
          _connectionStable = true;
          print('Connection is now stable');
          // Notify listeners about stable connection
          _messageController.add({
            'type': 'connection_status',
            'connected': true,
          });
        }
      });

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
          _connectionStable = false;
          print('WebSocket error: $error');
          
          // Cancel stability timer
          _connectionStabilityTimer?.cancel();
          
          // Only notify if we were previously stable
          if (_connectionStable) {
            _messageController.add({
              'type': 'connection_status',
              'connected': false,
            });
          }
          
          _handleError(error);
        },
        onDone: () {
          _connected = false;
          _connectionStable = false;
          print('WebSocket connection closed');
          
          // Cancel stability timer
          _connectionStabilityTimer?.cancel();
          
          // Only notify if we were previously stable
          if (_connectionStable) {
            _messageController.add({
              'type': 'connection_status',
              'connected': false,
            });
          }
          
          _handleClose();
        },
        cancelOnError: true,
      );
    } catch (e) {
      _connected = false;
      _connectionStable = false;
      print('Failed to establish WebSocket connection: $e');
      
      // Cancel stability timer
      _connectionStabilityTimer?.cancel();
      
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
    _connectionStable = false;
    _connectionStabilityTimer?.cancel();
    print('WebSocket disconnected');
  }

  void dispose() {
    disconnect();
    _connectionStabilityTimer?.cancel();
    _messageController.close();
  }

  // Method to start streaming a response
  void startStreamingResponse(String fullResponse, Map<String, dynamic> messageData) {
    if (_isStreaming) {
      stopStreaming();
    }
    
    _isStreaming = true;
    _currentStreamingIndex = 0;
    _currentStreamingText = '';
    _currentStreamingMessage = messageData;
    
    // Add thinking message first
    _addThinkingMessage();
    
    // Start streaming after thinking delay
    Future.delayed(const Duration(seconds: 2), () {
      if (_isStreaming) {
        _streamNextCharacter(fullResponse);
      }
    });
  }

  // Method to stop streaming
  void stopStreaming() {
    _isStreaming = false;
    _streamingTimer?.cancel();
    _streamingTimer = null;
    _currentStreamingIndex = 0;
    _currentStreamingText = '';
    _currentStreamingMessage = null;
  }

  // Add thinking message
  void _addThinkingMessage() {
    final thinkingMessage = {
      'fromUser': false,
      'text': 'thinking...',
      'time': DateTime.now().toString(),
      'method': null,
      'is_thinking': true,
    };
    
    _chatMessages.add(thinkingMessage);
    _messageController.add({'type': 'messages_updated'});
  }

  // Stream next character
  void _streamNextCharacter(String fullResponse) {
    if (!_isStreaming || _currentStreamingIndex >= fullResponse.length) {
      _finishStreaming();
      return;
    }

    _currentStreamingText += fullResponse[_currentStreamingIndex];
    _currentStreamingIndex++;

    // Update the thinking message with streaming text (accumulated)
    if (_chatMessages.isNotEmpty && _chatMessages.last['is_thinking'] == true) {
      _chatMessages.last['text'] = _currentStreamingText;
      _chatMessages.last['is_thinking'] = false;
      _messageController.add({'type': 'messages_updated'});
    }

    // Print prompt and current streaming response for debugging
    if (_currentStreamingMessage != null && _currentStreamingIndex == 1) {
      // Print prompt only once at the start
      print('Prompt: \'${_currentStreamingMessage!['prompt'] ?? ''}\'');
    }
    print('Streaming response so far: $_currentStreamingText');

    // Schedule next character
    _streamingTimer = Timer(const Duration(milliseconds: 50), () {
      _streamNextCharacter(fullResponse);
    });
  }

  // Finish streaming
  void _finishStreaming() {
    _isStreaming = false;
    _streamingTimer?.cancel();
    _streamingTimer = null;
    
    // Replace thinking message with final message
    if (_chatMessages.isNotEmpty && _currentStreamingMessage != null) {
      _chatMessages.last['text'] = _currentStreamingText;
      _chatMessages.last['is_thinking'] = false;
      _chatMessages.last['method'] = _currentStreamingMessage!['method'];
      _chatMessages.last['is_learning_resources'] = _currentStreamingMessage!['is_learning_resources'];
      // Print final response for debugging
      print('Final response: $_currentStreamingText');
    }
    
    _currentStreamingIndex = 0;
    _currentStreamingText = '';
    _currentStreamingMessage = null;
    
    _messageController.add({'type': 'messages_updated'});
  }
}
