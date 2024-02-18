from open3d import io, geometry, data
import open3d as o3d
class PointCloud3D():
  """
  class to read and operate on the pointcloud datasets taken from hand held devices 
  (meaning from volumetric scans unlike the lidar scans from air).
  - It can also take input from post colmap photo recalibration + NeRF reconstruction for eg.    
  """
  stored_pcd_dataset_path:str
  def __init__(self, pcd_dataset_path):
    self.stored_pcd_dataset_path = pcd_dataset_path
    self.stored_model: data.Dataset
    self.pcd = o3d.io.read_point_cloud(self.stored_pcd_dataset_path)
  def create_dataset_model(self,_url):
    """
    allows you to create a dataset model (if extracted from internet, this then can be used direclty in the read_point_cloud functions).
    _url: fetch the dataset from given website.
    """
    self.stored_model = data.Dataset(data_root=self.stored_pcd_dataset_path)
    self.stored_model.download_root = self.stored_pcd_dataset_path
    self.stored_model.extract_dir = _url
    
  def downsample_pcd(self,voxel_size: str):
    """
    returns the downsampled version of the actual point cloud provided in the following architecture.
    voxel_size: is the size of the point or density till which the given point cloud is to be downsampled.
    """
    
    return self.pcd.voxel_down_sample(voxel_size=voxel_size)
    
  def visualize_pcd(self,pcd_object, zoom, loopkat,  up, front):
      """
      shows the current version of the point cloud after the transformations
      pcd_object: is the corresponding pointcloud that you want to visualize after transformations
      zoom: natural value defining the  initial reference size of the point cloud that needs to be zoomed.
      loopkat: Is the the reference array of 3D coordinates [X,Y,Z] to be looking in order to look at pointcloud.
      up: its the reference point also for checking the pointcloud from initial reference point.
      """    
      o3d.visualization.draw_geometries(
        [pcd_object], zoom=zoom, lookat= loopkat, up=up, front=front
      )
  
      
  def get_boundation_box(self,min_point, max_point) -> geometry.AxisAlignedBoundingBox :
    """
    gets the boundation points that user wants to crop.

    min_point: is the reference (x,y,z) point (closer from the relative origin)
    max_point: is the reference (x,y,z) point (farther from the relative origin)
    """
    boundingBox = geometry.AxisAlignedBoundingBox()
    boundingBox.min_bound = min_point
    boundingBox.max_bound = max_point
    return boundingBox

  def crop_pcd(self, min_bound, max_bound, demo_name):
    """
    removes the portion defined by the bounding box and then stores this to the output
    boundingBox is the given boundation that is created by the user.
    demo_name: is the final name of the stored cropped pcd. we'll be setting up with the corresponding standards.
    """

    pcd = io.read_point_cloud(filename=self.stored_pcd_dataset_path)
    vol = geometry.crop_point_cloud(pcd,min_bound, max_bound)
    io.write_point_cloud(demo_name, vol)

  def combine_point_clouds(self,pcd_2, final_name, voxel_size):
      """
      this combines another point cloud with the current pcd being evaluated.
      the pcd_2 needs isalligned with the current pointcloud for uniform combination.
      voxel_size is the size of the point that you want to generate in the final format.
      """
      pcd_combined = geometry.PointCloud()
      for point_id in range(len(pcd_2)):
        self.stored_model[point_id].transform(pcd_2.nodes[point_id].pose)
        pcd_combined += self.stored_model[point_id]
      pcd_combined_down = pcd_combined.voxel_down_sample(voxel_size=voxel_size)
      io.write_point_cloud(final_name, pcd_combined_down)