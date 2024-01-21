from open3d import io, geometry, data, visualization


#class ModelCategory:



class PointCloud3D():
  stored_pcd_dataset_path:str
  def __init__(self, pcd_dataset_path, ):
    self.stored_pcd_dataset_path = pcd_dataset_path
    self.stored_model: data.Dataset

  def create_dataset_model(self,_url):
    """
    allows you to create a dataset model (if extracted from internet, this then can be used direclty in the read_point_cloud functions).
    _url: fetch the dataset from given website.
    """

    self.stored_model = data.Dataset(data_root=self.stored_pcd_dataset_path)
    self.stored_model.download_root = self.stored_pcd_dataset_path
    self.stored_model.extract_dir = _url

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

  def crop_pcd(self, boundingBox: geometry.AxisAlignedBoundingBox, demo_name):
    """
    removes the portion defined by the bounding box and then stores this to the output
    boundingBox is the given boundation that is created by the user.
    demo_name: is the final name of the stored cropped pcd. we'll be setting up with the corresponding standards.
    """

    pcd = io.read_point_cloud(filename=self.stored_pcd_dataset_path)
    vol = geometry.PointCloud.crop(pcd, boundingBox)
    io.write_point_cloud(demo_name, vol)

  def combine_point_clouds(self,pcd_2, final_name, voxel_size):
      """
      this combines another point cloud with the current pcd being evaluated.
      the pcd_2 needs isalligned with the current pointcloud for uniform combination.
      voxel_size is the 
      """
      pcd_combined = geometry.PointCloud()
      for point_id in range(len(pcd_2)):
        self.stored_model[point_id].transform(pcd_2.nodes[point_id].pose)
        pcd_combined += self.stored_model[point_id]
      pcd_combined_down = pcd_combined.voxel_down_sample(voxel_size=voxel_size)
      io.write_point_cloud(final_name, pcd_combined_down)


