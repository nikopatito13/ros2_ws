#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/lifecycle_node.hpp"

// Function that takes explicit node interfaces as arguments
void node_info(std::shared_ptr<rclcpp::node_interfaces::NodeBaseInterface> base_interface,
               std::shared_ptr<rclcpp::node_interfaces::NodeLoggingInterface> logging_interface)
{
  RCLCPP_INFO(logging_interface->get_logger(), "Node name: %s", base_interface->get_name());
}

// SimpleNode class inheriting from rclcpp::Node
class SimpleNode : public rclcpp::Node
{
public:
  SimpleNode(const std::string & node_name)
  : Node(node_name)
  {
  }
};  // Semicolon

// LifecycleTalker class inheriting from rclcpp_lifecycle::LifecycleNode
class LifecycleTalker : public rclcpp_lifecycle::LifecycleNode
{
public:
  explicit LifecycleTalker(const std::string & node_name, bool intra_process_comms = false)
  : rclcpp_lifecycle::LifecycleNode(node_name,
      rclcpp::NodeOptions().use_intra_process_comms(intra_process_comms))
  {}
};  // Semicolon

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  
  // Create instances of both node types
  auto node = std::make_shared<SimpleNode>("Simple_Node");
  auto lc_node = std::make_shared<LifecycleTalker>("Simple_LifeCycle_Node");
  
  // Call node_info with interfaces from SimpleNode
  node_info(node->get_node_base_interface(), node->get_node_logging_interface());
  
  // Call node_info with interfaces from LifecycleTalker
  node_info(lc_node->get_node_base_interface(), lc_node->get_node_logging_interface());
  
  // Spin using NodeBaseInterface to ensure compatibility
  rclcpp::spin_some(node->get_node_base_interface());
  rclcpp::spin_some(lc_node->get_node_base_interface());
  
  rclcpp::shutdown();
  return 0;
}