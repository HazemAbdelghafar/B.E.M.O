#include <dlib/dnn.h>
#include <dlib/image_processing/frontal_face_detector.h>
#include <dlib/image_processing/shape_predictor.h>
#include <dlib/image_io.h>
#include <dlib/gui_widgets.h>
#include <iostream>
#include <vector>

using namespace dlib;
using namespace std;

// Define the ResNet for face recognition
template <template <int, template<typename>class, int, typename> class block, int N, template<typename>class BN, typename SUBNET>
using residual = add_prev1<block<N, BN, 1, tag1<SUBNET>>>;

template <template <int, template<typename>class, int, typename> class block, int N, template<typename>class BN, typename SUBNET>
using residual_down = add_prev2<avg_pool<2, 2, 2, 2, skip1<tag2<block<N, BN, 2, tag1<SUBNET>>>>>>;

template <int N, template <typename> class BN, int stride, typename SUBNET>
using block = BN<con<N, 3, 3, 1, 1, relu<BN<con<N, 3, 3, stride, stride, SUBNET>>>>>;

template <int N, typename SUBNET> using ares = relu<residual<block, N, affine, SUBNET>>;
template <int N, typename SUBNET> using ares_down = relu<residual_down<block, N, affine, SUBNET>>;

template <typename SUBNET> using alevel0 = ares_down<256, SUBNET>;
template <typename SUBNET> using alevel1 = ares<256, ares<256, ares_down<256, SUBNET>>>;
template <typename SUBNET> using alevel2 = ares<128, ares<128, ares_down<128, SUBNET>>>;
template <typename SUBNET> using alevel3 = ares<64, ares<64, ares<64, ares_down<64, SUBNET>>>>;
template <typename SUBNET> using alevel4 = ares<32, ares<32, ares<32, SUBNET>>>;

using anet_type = loss_metric<fc_no_bias<128, avg_pool_everything<
                           alevel0<
                           alevel1<
                           alevel2<
                           alevel3<
                           alevel4<
                           max_pool<3, 3, 2, 2, relu<affine<con<32, 7, 7, 2, 2,
                           input_rgb_image_sized<150>
                           >>>>>>>>>>>>;

int main() try
{
    frontal_face_detector detector = get_frontal_face_detector();
    shape_predictor sp;
    deserialize("../shape_predictor_68_face_landmarks.dat") >> sp;
    anet_type net;
    deserialize("../dlib_face_recognition_resnet_model_v1.dat") >> net;

    std::vector<matrix<float, 0, 1>> user_descriptors;
    for (int i = 2; i < 7; ++i)
    {
        matrix<rgb_pixel> img;
        load_image(img, "../test" + to_string(i+1) + ".jpeg");  // Load the user's images

        // Detect face and compute descriptor
        auto faces = detector(img);
        if (faces.empty()) {
            cout << "No face found in user_photo_" << i+1 << ".jpeg!" << endl;
            continue;
        }

        auto shape = sp(img, faces[0]);
        matrix<rgb_pixel> face_chip;
        extract_image_chip(img, get_face_chip_details(shape, 150, 0.25), face_chip);

        // Display each detected face in a new window
        image_window win(face_chip, "Detected Face " + to_string(i+1));

        // Compute descriptor and store directly
        matrix<float, 0, 1> descriptor = net(face_chip);
        user_descriptors.push_back(descriptor);
        cout << "Captured face descriptor for user photo " << i+1 << endl;
    }

    // Ensure we have five descriptors
    if (user_descriptors.size() < 5) {
        cerr << "Insufficient user photos detected. Please check the images." << endl;
        return 1;
    }

    // Step 2: Recognize new test photo
    matrix<rgb_pixel> img;
    load_image(img, "../test9.jpeg");  // Load the test image

    auto faces = detector(img);
    if (faces.empty()) {
        cout << "No face found in test9.jpeg!" << endl;
        return 1;
    }

    auto shape = sp(img, faces[0]);
    matrix<rgb_pixel> face_chip;
    extract_image_chip(img, get_face_chip_details(shape, 150, 0.25), face_chip);

    // Display the test photo detected face
    image_window test_win(face_chip, "Test Photo Detected Face");

    // Compute descriptor for test photo directly
    matrix<float, 0, 1> test_descriptor = net(face_chip);

    // Compare the test photo descriptor with each stored user descriptor
    bool is_user = false;
    for (const auto& user_descriptor : user_descriptors)
    {
        double distance = length(user_descriptor - test_descriptor);
        if (distance < 0.6)
        {
            is_user = true;
            break;
        }
    }

    if (is_user)
        cout << "This photo matches the user!" << endl;
    else
        cout << "This photo does NOT match the user." << endl;

    return 0;
}
catch (std::exception& e)
{
    cout << "Exception: " << e.what() << endl;
    return 1;
}
