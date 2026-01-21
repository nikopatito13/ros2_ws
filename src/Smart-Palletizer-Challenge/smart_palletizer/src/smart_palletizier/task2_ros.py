#!/usr/bin/env python3
import os
import rclpy
from rclpy.node import Node
import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import binned_statistic_2d
from scipy.interpolate import griddata

class BoxVisualizationNode(Node):

    def __init__(self):
        super().__init__('box_visualization_node')
        
        # Declare and get parameter with default
        self.declare_parameter('input_dir', os.path.expanduser('~/ros2_ws/src/project/data/'))
        self.root_dir = self.get_parameter('input_dir').get_parameter_value().string_value
        
        if not os.path.exists(self.root_dir):
            self.get_logger().fatal(f"Input directory not found: {self.root_dir}")
            rclpy.shutdown()
            return
        
        box_data = self.load_point_clouds(self.root_dir)
        if box_data:
            self.visualize_boxes(box_data)
            self.get_logger().info("Visualization complete")
        else:
            self.get_logger().warn("No valid point cloud files found")

    def load_point_clouds(self, root_dir):
        #Load and validate box point clouds from directory structure
        box_data = {}
        
        for dirpath, _, filenames in os.walk(root_dir):
            for fname in sorted(filenames):
                if not (fname.endswith(".ply") and "_raw" in fname):
                    continue
                    
                ply_path = os.path.join(dirpath, fname)
                self.get_logger().info(f"Loading: {ply_path}")
                
                try:
                    pcd = o3d.io.read_point_cloud(ply_path)
                    box_data[fname.split('.')[0]] = np.asarray(pcd.points)
                except Exception as e:
                    self.get_logger().error(f"Failed to load {ply_path}: {str(e)}")
        
        return box_data

    def create_surface_grid(self, points, grid_size=0.02):
        #Convert point cloud to grid surface using binned statistics
        x, y, z = points.T
        x_min, x_max = np.min(x), np.max(x)
        y_min, y_max = np.min(y), np.max(y)

        xi = np.arange(x_min, x_max + grid_size, grid_size)
        yi = np.arange(y_min, y_max + grid_size, grid_size)
        
        # Use binned_statistic_2d to get maximum values
        statistic, x_edge, y_edge, _ = binned_statistic_2d(
            x, y, z,
            statistic='max',
            bins=[xi, yi]
        )
        
        # Transpose to match meshgrid orientation
        Z = statistic.T
        X, Y = np.meshgrid(x_edge[:-1], y_edge[:-1])
        
        return X, Y, Z

    def visualize_boxes(self, box_data):
        #Visualize all boxes in a single optimized 3D plot
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        colors = plt.cm.tab20(np.linspace(0, 1, len(box_data)))

        for (box_id, points), color in zip(box_data.items(), colors):
            X, Y, Z = self.create_surface_grid(points)
            ax.plot_surface(X, Y, Z, color=color, alpha=0.9, linewidth=0.2, antialiased=True, edgecolor='k', rstride=1, cstride=1)
            ax.plot([], [], [], color=color, label=f"Box {box_id}")

        ax.set(xlabel='X', ylabel='Y', zlabel='Z')
        ax.view_init(elev=20, azim=-60)
        ax.legend(loc='center left', bbox_to_anchor=(1.05, 0.5))
        
        plt.tight_layout()
        plt.savefig('boxes_visualization.svg', format='svg', dpi=300)
        plt.show()


def main(args=None):
    rclpy.init(args=args)
    node = BoxVisualizationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
    