#### import the simple module from the paraview
from paraview.simple import *
import glob
import re

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

# for visualising Capsaspora simulations on a small domain, [0, 360] x [0, 360] um
def Capsaspora360(sim_folder,folder_save_video,save_anim):

  full_sim_path = sim_folder+'/'

  #### disable automatic camera reset on 'Show'
  paraview.simple._DisableFirstRenderCameraReset()

  ResetSession()

  # get active view
  renderView1 = GetActiveViewOrCreate('RenderView')

  # Hide orientation axes
  renderView1.OrientationAxesVisibility = 0

  num_frames = len(glob.glob(full_sim_path+'results_from_time_0/results_*.vtu'))
  print('num frames: '+str(num_frames))

  # create a new 'XML Unstructured Grid Reader'
  results_ = XMLUnstructuredGridReader(registrationName='results_*', FileName=natural_sort(glob.glob(full_sim_path+'results_from_time_0/results_*.vtu') ) )
  results_.CellArrayStatus = []
  results_.PointArrayStatus = ['Prolif Cell types', 'Legacy Cell types', 'Process rank', 'fbs']
  results_.TimeArray = 'TimeValue'

  # get animation scene
  animationScene1 = GetAnimationScene()

  # update animation scene based on data timesteps
  animationScene1.UpdateAnimationUsingDataTimeSteps()

  # create a new 'XML Unstructured Grid Reader'
  pde_results_fbs_ = XMLUnstructuredGridReader(registrationName='pde_results_fbs_*', FileName= natural_sort(glob.glob(full_sim_path+'results_from_time_0/pde_results_fbs_*.vtu')))
  pde_results_fbs_.CellArrayStatus = []
  pde_results_fbs_.PointArrayStatus = ['fbs']
  pde_results_fbs_.TimeArray = 'TimeValue'

  # create a new 'Transform'
  transform1 = Transform(registrationName='Transform1', Input=pde_results_fbs_)
  transform1.Transform = 'Transform'
  transform1.TransformAllInputVectors = 1

  # Properties modified on transform1.Transform
  transform1.Transform.Translate = [0.0, 0.0, -100.0]
  transform1.Transform.Rotate = [0.0, 0.0, 0.0]
  transform1.Transform.Scale = [3.0, 3.0, 1.0]

  # show data in view
  transform1Display = Show(transform1, renderView1, 'UnstructuredGridRepresentation')

  # hide data in view
  Hide(pde_results_fbs_, renderView1)

  # update the view to ensure updated data information
  renderView1.Update()

  # set scalar coloring
  ColorBy(transform1Display, ('POINTS', 'fbs'))

  # show color bar/color legend
  transform1Display.SetScalarBarVisibility(renderView1, True)

  # get color transfer function/color map for 'fbs'
  fbsLUT = GetColorTransferFunction('fbs')

  # get opacity transfer function/opacity map for 'fbs'
  fbsPWF = GetOpacityTransferFunction('fbs')

  fbsLUT.AutomaticRescaleRangeMode = 'Never'

  # Rescale transfer function
  fbsLUT.RescaleTransferFunction(0.0, 2.0)

  # Rescale transfer function
  fbsPWF.RescaleTransferFunction(0.0, 2.0)

  # get color legend/bar for fbsLUT in view renderView1
  fbsLUTColorBar = GetScalarBar(fbsLUT, renderView1)

  renderView1.Update()

  # set active source
  SetActiveSource(results_)

  # create a new 'Transform'
  transform2 = Transform(registrationName='Transform2', Input=results_)
  transform2.Transform = 'Transform'
  transform2.TransformAllInputVectors = 1

  # init the 'Transform' selected for 'Transform'
  transform2.Transform.Translate = [0.0, 0.0, 0.0]
  transform2.Transform.Rotate = [0.0, 0.0, 0.0]
  transform2.Transform.Scale = [3.0, 3.0, 1.0]

  # show data in view
  transform2Display = Show(transform2, renderView1, 'UnstructuredGridRepresentation')
 
  # hide data in view
  Hide(results_, renderView1)

  # update the view to ensure updated data information
  renderView1.Update()

  # set scalar coloring
  ColorBy(transform2Display, ('POINTS', 'fbs'))

  # show color bar/color legend
  transform2Display.SetScalarBarVisibility(renderView1, True)

  # change representation type
  transform2Display.SetRepresentationType('Point Gaussian')

  # Properties modified on transform2Display
  transform2Display.GaussianRadius = 3.0
  
  # set active source
  SetActiveSource(transform2)

   # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XTitle = '$\\mu m$'
  renderView1.AxesGrid.YTitle = '$\\mu m$     '
  renderView1.AxesGrid.XTitleColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.YTitleColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.GridColor = [0.0, 0.0, 0.0]

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XLabelColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.YLabelColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.XAxisUseCustomLabels = 1
  renderView1.AxesGrid.XAxisLabels = [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0]

  # # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.YAxisUseCustomLabels = 1
  renderView1.AxesGrid.YAxisLabels = [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0]

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.UseCustomBounds = 1
  renderView1.AxesGrid.CustomBounds = [0.0, 360.0, 0.0, 360.0, 0.0, 1.0]

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XLabelFontSize = 25
  renderView1.AxesGrid.YLabelFontSize = 25

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XTitleFontSize = 25
  renderView1.AxesGrid.YTitleFontSize = 25

  # Rescale transfer function
  fbsLUT.RescaleTransferFunction(0.0, 2.0)

  # Rescale transfer function
  fbsPWF.RescaleTransferFunction(0.0, 2.0)

  # get color legend/bar for fbsLUT in view renderView1
  fbsLUTColorBar = GetScalarBar(fbsLUT, renderView1)

  # change scalar bar placement
  fbsLUTColorBar.WindowLocation = 'Any Location'

  fbsLUTColorBar.Title = 'FBS'
  fbsLUTColorBar.TitleJustification = 'Centered'
  fbsLUTColorBar.HorizontalTitle = 1
  fbsLUTColorBar.AutomaticLabelFormat = 0
  fbsLUTColorBar.LabelFormat = '%-#6.1f'
  fbsLUTColorBar.AddRangeLabels = 0
  fbsLUTColorBar.ScalarBarLength = 0.4

  # get color legend/bar for fbsLUT in view renderView1
  fbsLUTColorBar = GetScalarBar(fbsLUT, renderView1)

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.TitleColor = [0.0, 0.0, 0.0]

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.LabelColor = [0.0, 0.0, 0.0]

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.TitleFontSize = 15
  fbsLUTColorBar.LabelFontSize = 13

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.TextPosition = 'Ticks left/bottom, annotations right/top'

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.DrawTickMarks = 1
  fbsLUTColorBar.DrawTickLabels = 0
  fbsLUTColorBar.UseCustomLabels = 1

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.CustomLabels = [0.0, 0.5, 1.0, 1.5, 2.0]

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.Position = [0.88, 0.2]
  fbsLUTColorBar.ScalarBarThickness = 15

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.DrawTickMarks = 0

  fbsLUT.IndexedColors = [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
  fbsLUT.IndexedOpacities = [1.0, 1.0, 1.0, 1.0]

  # Properties modified on fbsLUT
  fbsLUT.Annotations = ['0', '0%', '0.5', '2.5%', '1', '5%', '1.5', '7.5%', '2', '10%']

  # create a new 'Annotate Time Filter'
  annotateTimeFilter1 = AnnotateTimeFilter(registrationName='AnnotateTimeFilter1', Input=transform2)
  annotateTimeFilter1.Format = 'Time: {time:f}'
  annotateTimeFilter1.Shift = 0.0
  annotateTimeFilter1.Scale = 1.0

  # Properties modified on annotateTimeFilter1
  annotateTimeFilter1.Format = 'Time: {time:.2f} h'
  annotateTimeFilter1.Scale = 0.06666666

  # show data in view
  annotateTimeFilter1Display = Show(annotateTimeFilter1, renderView1, 'TextSourceRepresentation')

  annotateTimeFilter1Display.WindowLocation = 'Upper Left Corner'
  annotateTimeFilter1Display.Position = [0.05, 0.05]
  annotateTimeFilter1Display.Color = [0.0, 0.0, 0.0]

  # update the view to ensure updated data information
  renderView1.Update()

  # Properties modified on annotateTimeFilter1Display
  annotateTimeFilter1Display.FontSize = 40

  # get layout
  layout1 = GetLayout()

  # layout/tab size in pixels
  layout1.SetSize(836, 716)

  # current camera placement for renderView1
  renderView1.InteractionMode = '2D'
  renderView1.CameraPosition = [182.82, 182.38, 10000.0]
  renderView1.CameraFocalPoint = [182.82, 182.38, 0.0]
  renderView1.CameraParallelScale = 211.9890761754707
  renderView1.Update()

  # save animation

  sim_folder_short = sim_folder.split("/")[-1:]
  sim_folder_short2 = sim_folder_short[0]
  
  if save_anim:
    print('Animation video is written to: '+folder_save_video+'/'+sim_folder_short2+'.avi')
    SaveAnimation(folder_save_video+'/'+sim_folder_short2+'.avi', renderView1, ImageResolution=[1672, 1432],
        FontScaling='Scale fonts proportionally',
        OverrideColorPalette='WhiteBackground',
        StereoMode='No change',
        TransparentBackground=0,
        FrameRate=7,
        FrameWindow=[0, num_frames - 1], 
        # FFMPEG options
        Compression=1,
        Quality='2')

  #--------------------------------------------

# for visualising Capsaspora simulations on a large domain, [0, 1080] x [0, 1080] um
def Capsaspora1080(sim_folder,folder_save_video,save_anim):

  full_sim_path = sim_folder+'/'

  #### disable automatic camera reset on 'Show'
  paraview.simple._DisableFirstRenderCameraReset()

  ResetSession()

  # get active view
  renderView1 = GetActiveViewOrCreate('RenderView')

  # Hide orientation axes
  renderView1.OrientationAxesVisibility = 0

  num_frames = len(glob.glob(full_sim_path+'results_from_time_0/results_*.vtu'))
  print('num frames: '+str(num_frames))

  # create a new 'XML Unstructured Grid Reader'
  results_ = XMLUnstructuredGridReader(registrationName='results_*', FileName=natural_sort(glob.glob(full_sim_path+'results_from_time_0/results_*.vtu') ) )
  results_.CellArrayStatus = []
  results_.PointArrayStatus = ['Prolif Cell types', 'Legacy Cell types', 'Process rank', 'fbs']
  results_.TimeArray = 'TimeValue'

  # get animation scene
  animationScene1 = GetAnimationScene()

  # update animation scene based on data timesteps
  animationScene1.UpdateAnimationUsingDataTimeSteps()

  # create a new 'XML Unstructured Grid Reader'
  pde_results_fbs_ = XMLUnstructuredGridReader(registrationName='pde_results_fbs_*', FileName= natural_sort(glob.glob(full_sim_path+'results_from_time_0/pde_results_fbs_*.vtu')))
  pde_results_fbs_.CellArrayStatus = []
  pde_results_fbs_.PointArrayStatus = ['fbs']
  pde_results_fbs_.TimeArray = 'TimeValue'

  # create a new 'Transform'
  transform1 = Transform(registrationName='Transform1', Input=pde_results_fbs_)
  transform1.Transform = 'Transform'
  transform1.TransformAllInputVectors = 1

  # Properties modified on transform1.Transform
  transform1.Transform.Translate = [0.0, 0.0, -100.0]
  transform1.Transform.Rotate = [0.0, 0.0, 0.0]
  transform1.Transform.Scale = [3.0, 3.0, 1.0]

  # show data in view
  transform1Display = Show(transform1, renderView1, 'UnstructuredGridRepresentation')

  # hide data in view
  Hide(pde_results_fbs_, renderView1)

  # update the view to ensure updated data information
  renderView1.Update()

  # set scalar coloring
  ColorBy(transform1Display, ('POINTS', 'fbs'))

  # show color bar/color legend
  transform1Display.SetScalarBarVisibility(renderView1, True)

  # get color transfer function/color map for 'fbs'
  fbsLUT = GetColorTransferFunction('fbs')

  # get opacity transfer function/opacity map for 'fbs'
  fbsPWF = GetOpacityTransferFunction('fbs')

  fbsLUT.AutomaticRescaleRangeMode = 'Never'

  # Rescale transfer function
  fbsLUT.RescaleTransferFunction(0.0, 2.0)

  # Rescale transfer function
  fbsPWF.RescaleTransferFunction(0.0, 2.0)

  # get color legend/bar for fbsLUT in view renderView1
  fbsLUTColorBar = GetScalarBar(fbsLUT, renderView1)

  renderView1.Update()

  # set active source
  SetActiveSource(results_)

  # create a new 'Transform'
  transform2 = Transform(registrationName='Transform2', Input=results_)
  transform2.Transform = 'Transform'
  transform2.TransformAllInputVectors = 1

  # init the 'Transform' selected for 'Transform'
  transform2.Transform.Translate = [0.0, 0.0, 0.0]
  transform2.Transform.Rotate = [0.0, 0.0, 0.0]
  transform2.Transform.Scale = [3.0, 3.0, 1.0]

  # show data in view
  transform2Display = Show(transform2, renderView1, 'UnstructuredGridRepresentation')
 
  # hide data in view
  Hide(results_, renderView1)

  # update the view to ensure updated data information
  renderView1.Update()

  # set scalar coloring
  ColorBy(transform2Display, ('POINTS', 'fbs'))

  # show color bar/color legend
  transform2Display.SetScalarBarVisibility(renderView1, True)

  # change representation type
  transform2Display.SetRepresentationType('Point Gaussian')

  # Properties modified on transform2Display
  transform2Display.GaussianRadius = 3.0
  
  # set active source
  SetActiveSource(transform2)

   # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XTitle = '$\\mu m$'
  renderView1.AxesGrid.YTitle = '$\\mu m$     '
  renderView1.AxesGrid.XTitleColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.YTitleColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.GridColor = [0.0, 0.0, 0.0]

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XLabelColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.YLabelColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.XAxisUseCustomLabels = 1
  renderView1.AxesGrid.XAxisLabels = [0.0, 200.0, 400.0, 600.0, 800.0, 1000.0]

  # # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.YAxisUseCustomLabels = 1
  renderView1.AxesGrid.YAxisLabels = [0.0, 200.0, 400.0, 600.0, 800.0, 1000.0]

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.UseCustomBounds = 1
  renderView1.AxesGrid.CustomBounds = [0.0, 1080.0, 0.0, 1080.0, 0.0, 1.0]

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XLabelFontSize = 25
  renderView1.AxesGrid.YLabelFontSize = 25

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XTitleFontSize = 25
  renderView1.AxesGrid.YTitleFontSize = 25

  # Rescale transfer function
  fbsLUT.RescaleTransferFunction(0.0, 2.0)

  # Rescale transfer function
  fbsPWF.RescaleTransferFunction(0.0, 2.0)

  # get color legend/bar for fbsLUT in view renderView1
  fbsLUTColorBar = GetScalarBar(fbsLUT, renderView1)

  # change scalar bar placement
  fbsLUTColorBar.WindowLocation = 'Any Location'

  fbsLUTColorBar.Title = 'FBS'
  fbsLUTColorBar.TitleJustification = 'Centered'
  fbsLUTColorBar.HorizontalTitle = 1
  fbsLUTColorBar.AutomaticLabelFormat = 0
  fbsLUTColorBar.LabelFormat = '%-#6.1f'
  fbsLUTColorBar.AddRangeLabels = 0
  fbsLUTColorBar.ScalarBarLength = 0.4

  # get color legend/bar for fbsLUT in view renderView1
  fbsLUTColorBar = GetScalarBar(fbsLUT, renderView1)

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.TitleColor = [0.0, 0.0, 0.0]

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.LabelColor = [0.0, 0.0, 0.0]

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.TitleFontSize = 15
  fbsLUTColorBar.LabelFontSize = 13

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.TextPosition = 'Ticks left/bottom, annotations right/top'

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.DrawTickMarks = 1
  fbsLUTColorBar.DrawTickLabels = 0
  fbsLUTColorBar.UseCustomLabels = 1

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.CustomLabels = [0.0, 0.5, 1.0, 1.5, 2.0]

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.Position = [0.88, 0.2]
  fbsLUTColorBar.ScalarBarThickness = 15

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.DrawTickMarks = 0

  fbsLUT.IndexedColors = [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
  fbsLUT.IndexedOpacities = [1.0, 1.0, 1.0, 1.0]

  # Properties modified on fbsLUT
  fbsLUT.Annotations = ['0', '0%', '0.5', '2.5%', '1', '5%', '1.5', '7.5%', '2', '10%']

  # create a new 'Annotate Time Filter'
  annotateTimeFilter1 = AnnotateTimeFilter(registrationName='AnnotateTimeFilter1', Input=transform2)
  annotateTimeFilter1.Format = 'Time: {time:f}'
  annotateTimeFilter1.Shift = 0.0
  annotateTimeFilter1.Scale = 1.0

  # Properties modified on annotateTimeFilter1
  annotateTimeFilter1.Format = 'Time: {time:.2f} h'
  annotateTimeFilter1.Scale = 0.06666666

  # show data in view
  annotateTimeFilter1Display = Show(annotateTimeFilter1, renderView1, 'TextSourceRepresentation')

  annotateTimeFilter1Display.WindowLocation = 'Upper Left Corner'
  annotateTimeFilter1Display.Position = [0.05, 0.05]
  annotateTimeFilter1Display.Color = [0.0, 0.0, 0.0]

  # update the view to ensure updated data information
  renderView1.Update()

  # Properties modified on annotateTimeFilter1Display
  annotateTimeFilter1Display.FontSize = 40

  # get layout
  layout1 = GetLayout()

  # layout/tab size in pixels
  layout1.SetSize(836, 716)

  # current camera placement for renderView1
  renderView1.InteractionMode = '2D'
  renderView1.CameraPosition = [547, 540, 10000.0]
  renderView1.CameraFocalPoint = [547, 540, 0.0]
  renderView1.CameraParallelScale = 625

  renderView1.Update()

  # save animation

  sim_folder_short = sim_folder.split("/")[-1:]
  sim_folder_short2 = sim_folder_short[0]
  
  if save_anim:
    print('Animation video is written to: '+folder_save_video+'/'+sim_folder_short2+'.avi')
    SaveAnimation(folder_save_video+'/'+sim_folder_short2+'.avi', renderView1, ImageResolution=[1672, 1432],
        FontScaling='Scale fonts proportionally',
        OverrideColorPalette='WhiteBackground',
        StereoMode='No change',
        TransparentBackground=0,
        FrameRate=7,
        FrameWindow=[0, num_frames - 1], 
        # FFMPEG options
        Compression=1,
        Quality='2')

  #--------------------------------------------

# for visualising Capsaspora simulations on a small domain, [0, 360] x [0, 360] um
# with cells coloured in local cell density
def Capsaspora360_CellDensity(sim_folder,folder_save_video,save_anim):

  full_sim_path = sim_folder+'/'

  #### disable automatic camera reset on 'Show'
  paraview.simple._DisableFirstRenderCameraReset()

  ResetSession()

  # get active view
  renderView1 = GetActiveViewOrCreate('RenderView')

  # Hide orientation axes
  renderView1.OrientationAxesVisibility = 0

  num_frames = len(glob.glob(full_sim_path+'results_from_time_0/results_*.vtu'))
  print('num frames: '+str(num_frames))

  # create a new 'XML Unstructured Grid Reader'
  results_ = XMLUnstructuredGridReader(registrationName='results_*', FileName=natural_sort(glob.glob(full_sim_path+'results_from_time_0/results_*.vtu') ) )
  results_.CellArrayStatus = []
  results_.PointArrayStatus = ['Prolif Cell types', 'Legacy Cell types', 'Process rank', 'fbs']
  results_.TimeArray = 'TimeValue'

  # get animation scene
  animationScene1 = GetAnimationScene()

  # update animation scene based on data timesteps
  animationScene1.UpdateAnimationUsingDataTimeSteps()

  # create a new 'XML Unstructured Grid Reader'
  pde_results_fbs_ = XMLUnstructuredGridReader(registrationName='pde_results_fbs_*', FileName= natural_sort(glob.glob(full_sim_path+'results_from_time_0/pde_results_fbs_*.vtu')))
  pde_results_fbs_.CellArrayStatus = []
  pde_results_fbs_.PointArrayStatus = ['fbs']
  pde_results_fbs_.TimeArray = 'TimeValue'

  # create a new 'Transform'
  transform1 = Transform(registrationName='Transform1', Input=pde_results_fbs_)
  transform1.Transform = 'Transform'
  transform1.TransformAllInputVectors = 1

  # Properties modified on transform1.Transform
  transform1.Transform.Translate = [0.0, 0.0, -100.0]
  transform1.Transform.Rotate = [0.0, 0.0, 0.0]
  transform1.Transform.Scale = [3.0, 3.0, 1.0]

  # show data in view
  transform1Display = Show(transform1, renderView1, 'UnstructuredGridRepresentation')

  # hide data in view
  Hide(pde_results_fbs_, renderView1)

  # update the view to ensure updated data information
  renderView1.Update()

  # set scalar coloring
  ColorBy(transform1Display, ('POINTS', 'fbs'))

  # show color bar/color legend
  transform1Display.SetScalarBarVisibility(renderView1, True)

  # get color transfer function/color map for 'fbs'
  fbsLUT = GetColorTransferFunction('fbs')

  # get opacity transfer function/opacity map for 'fbs'
  fbsPWF = GetOpacityTransferFunction('fbs')

  fbsLUT.AutomaticRescaleRangeMode = 'Never'

  # Rescale transfer function
  fbsLUT.RescaleTransferFunction(0.0, 2.0)

  # Rescale transfer function
  fbsPWF.RescaleTransferFunction(0.0, 2.0)

  # get color legend/bar for fbsLUT in view renderView1
  fbsLUTColorBar = GetScalarBar(fbsLUT, renderView1)

  renderView1.Update()

  # set active source
  SetActiveSource(results_)

  # create a new 'Transform'
  transform2 = Transform(registrationName='Transform2', Input=results_)
  transform2.Transform = 'Transform'
  transform2.TransformAllInputVectors = 1

  # init the 'Transform' selected for 'Transform'
  transform2.Transform.Translate = [0.0, 0.0, 0.0]
  transform2.Transform.Rotate = [0.0, 0.0, 0.0]
  transform2.Transform.Scale = [3.0, 3.0, 1.0]

  # show data in view
  transform2Display = Show(transform2, renderView1, 'UnstructuredGridRepresentation')
 
  # hide data in view
  Hide(results_, renderView1)

  # update the view to ensure updated data information
  renderView1.Update()

  # set scalar coloring
  ColorBy(transform2Display, ('POINTS', 'fbs'))

  # show color bar/color legend
  transform2Display.SetScalarBarVisibility(renderView1, True)

  # change representation type
  transform2Display.SetRepresentationType('Point Gaussian')

  # Properties modified on transform2Display
  transform2Display.GaussianRadius = 3.0
  
  # set active source
  SetActiveSource(transform2)

   # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XTitle = '$\\mu m$'
  renderView1.AxesGrid.YTitle = '$\\mu m$     '
  renderView1.AxesGrid.XTitleColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.YTitleColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.GridColor = [0.0, 0.0, 0.0]

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XLabelColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.YLabelColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.XAxisUseCustomLabels = 1
  renderView1.AxesGrid.XAxisLabels = [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0]

  # # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.YAxisUseCustomLabels = 1
  renderView1.AxesGrid.YAxisLabels = [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0]

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.UseCustomBounds = 1
  renderView1.AxesGrid.CustomBounds = [0.0, 360.0, 0.0, 360.0, 0.0, 1.0]

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XLabelFontSize = 25
  renderView1.AxesGrid.YLabelFontSize = 25

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XTitleFontSize = 25
  renderView1.AxesGrid.YTitleFontSize = 25

  # Rescale transfer function
  fbsLUT.RescaleTransferFunction(0.0, 2.0)

  # Rescale transfer function
  fbsPWF.RescaleTransferFunction(0.0, 2.0)

  # get color legend/bar for fbsLUT in view renderView1
  fbsLUTColorBar = GetScalarBar(fbsLUT, renderView1)

  # change scalar bar placement
  fbsLUTColorBar.WindowLocation = 'Any Location'

  fbsLUTColorBar.Title = 'FBS\n'
  fbsLUTColorBar.TitleJustification = 'Centered'
  fbsLUTColorBar.HorizontalTitle = 1
  fbsLUTColorBar.AutomaticLabelFormat = 0
  fbsLUTColorBar.LabelFormat = '%-#6.1f'
  fbsLUTColorBar.AddRangeLabels = 0
  fbsLUTColorBar.ScalarBarLength = 0.3

  # get color legend/bar for fbsLUT in view renderView1
  fbsLUTColorBar = GetScalarBar(fbsLUT, renderView1)

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.TitleColor = [0.0, 0.0, 0.0]

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.LabelColor = [0.0, 0.0, 0.0]

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.TitleFontSize = 12
  fbsLUTColorBar.LabelFontSize = 10

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.TextPosition = 'Ticks left/bottom, annotations right/top'

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.DrawTickLabels = 0
  fbsLUTColorBar.UseCustomLabels = 1

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.CustomLabels = [0.0, 0.5, 1.0, 1.5, 2.0]

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.Position = [0.88, 0.1]
  fbsLUTColorBar.ScalarBarThickness = 15

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.DrawTickMarks = 0

  fbsLUT.IndexedColors = [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
  fbsLUT.IndexedOpacities = [1.0, 1.0, 1.0, 1.0]

  # Properties modified on fbsLUT
  fbsLUT.Annotations = ['0', '0%', '0.5', '2.5%', '1', '5%', '1.5', '7.5%', '2', '10%']

  # create a new 'Annotate Time Filter'
  annotateTimeFilter1 = AnnotateTimeFilter(registrationName='AnnotateTimeFilter1', Input=transform2)
  annotateTimeFilter1.Format = 'Time: {time:f}'
  annotateTimeFilter1.Shift = 0.0
  annotateTimeFilter1.Scale = 1.0

  # Properties modified on annotateTimeFilter1
  annotateTimeFilter1.Format = 'Time: {time:.2f} h'
  annotateTimeFilter1.Scale = 0.06666666

  # show data in view
  annotateTimeFilter1Display = Show(annotateTimeFilter1, renderView1, 'TextSourceRepresentation')

  annotateTimeFilter1Display.WindowLocation = 'Upper Left Corner'
  annotateTimeFilter1Display.Position = [0.05, 0.05]
  annotateTimeFilter1Display.Color = [0.0, 0.0, 0.0]

  # update the view to ensure updated data information
  renderView1.Update()

  # Properties modified on annotateTimeFilter1Display
  annotateTimeFilter1Display.FontSize = 40

  # Compute local cell density and set it as the cell colour 
  # set active source
  SetActiveSource(transform2)

  # get display properties
  transform2Display = GetDisplayProperties(transform2, view=renderView1)

  # create a new 'Programmable Filter'
  programmableFilter1 = ProgrammableFilter(registrationName='ProgrammableFilter1', Input=transform2)

  # Properties modified on programmableFilter1
  programmableFilter1.Script = """
  import numpy as np
  from vtkmodules.numpy_interface import algorithms as algs
  from vtkmodules.util import numpy_support

  # Get input data
  input_data = inputs[0]
  # Extract point coordinates
  points = input_data.Points  

  # Radius for circular neighborhood (Modify as needed)
  circle_radius = 10  # Define the radius around each cell
  circle_area = np.pi * (circle_radius ** 2)  # Area of the circular neighborhood

  # Convert points to a NumPy array
  num_points = points.shape[0]
  density_values = np.zeros(num_points)

  # Compute density for each point
  for i, (x, y, z) in enumerate(points):
      # Count neighboring points within the circle
      neighbor_count = np.sum((points[:, 0] - x) ** 2 + (points[:, 1] - y) ** 2 <= circle_radius ** 2)
      
      # Compute density as number of neighbors per unit area
      density_values[i] = neighbor_count / circle_area

  # Convert NumPy array to VTK and add it to the output
  output = self.GetOutput()
  density_array = numpy_support.numpy_to_vtk(density_values, deep=True)
  density_array.SetName("Particle Density")
  output.GetPointData().AddArray(density_array)"""
  programmableFilter1.RequestInformationScript = ''
  programmableFilter1.RequestUpdateExtentScript = ''
  programmableFilter1.PythonPath = ''

  # show data in view
  programmableFilter1Display = Show(programmableFilter1, renderView1, 'UnstructuredGridRepresentation')
  programmableFilter1Display.OpacityArrayName = ['POINTS', 'Particle Density']

  # hide data in view
  Hide(transform2, renderView1)

  # update the view to ensure updated data information
  renderView1.Update()

  # change representation type
  programmableFilter1Display.SetRepresentationType('Point Gaussian')

  # set scalar coloring
  ColorBy(programmableFilter1Display, ('POINTS', 'Particle Density'))

  # rescale color and/or opacity maps used to include current data range
  programmableFilter1Display.RescaleTransferFunctionToDataRange(True, False)

  # show color bar/color legend
  programmableFilter1Display.SetScalarBarVisibility(renderView1, True)

  # get color transfer function/color map for 'ParticleDensity'
  particleDensityLUT = GetColorTransferFunction('ParticleDensity')

  # get opacity transfer function/opacity map for 'ParticleDensity'
  particleDensityPWF = GetOpacityTransferFunction('ParticleDensity')

  # Properties modified on programmableFilter1Display
  programmableFilter1Display.GaussianRadius = 3.0

  # get color legend/bar for particleDensityLUT in view renderView1
  particleDensityLUTColorBar = GetScalarBar(particleDensityLUT, renderView1)

  # change scalar bar placement
  particleDensityLUTColorBar.WindowLocation = 'Any Location'

  # change scalar bar placement
  particleDensityLUTColorBar.Position = [0.88, 0.53]

  # Rescale transfer function
  particleDensityLUT.RescaleTransferFunction(0.0, 0.06)

  # Properties modified on particleDensityLUTColorBar
  particleDensityLUTColorBar.TextPosition = 'Ticks left/bottom, annotations right/top'
  # particleDensityLUTColorBar.DrawTickMarks = 1
  particleDensityLUTColorBar.Title = 'cell \ndensity\n'
  particleDensityLUTColorBar.ComponentTitle = ''
  particleDensityLUTColorBar.TitleColor = [0.0, 0.0, 0.0]
  particleDensityLUTColorBar.LabelColor = [0.0, 0.0, 0.0]
  particleDensityLUTColorBar.ScalarBarThickness = 15
  particleDensityLUTColorBar.AddRangeLabels = 0
  particleDensityLUTColorBar.ScalarBarLength = 0.3
  particleDensityLUTColorBar.TitleJustification = 'Left'

  # Properties modified on particleDensityLUT
  particleDensityLUT.RGBPoints = [0.0, 0.0, 0.0, 0.0, 0.02, 0.647, 0.019, 0.988, 0.04, 0.635, 0.788, 0.0, 0.05, 1.0, 1.0, 0.0, 0.06, 1.0, 1.0, 0.0,]

  # Properties modified on particleDensityLUTColorBar
  particleDensityLUTColorBar.HorizontalTitle = 1

  # Properties modified on particleDensityLUTColorBar
  particleDensityLUTColorBar.TitleFontSize = 12
  particleDensityLUTColorBar.LabelFontSize = 10
  particleDensityLUTColorBar.RangeLabelFormat = '%-#6.2f'

  # Properties modified on fbsLUTColorBar
  particleDensityLUTColorBar.DrawTickLabels = 0
  particleDensityLUTColorBar.DrawTickMarks = 0
  particleDensityLUTColorBar.UseCustomLabels = 1
  particleDensityLUTColorBar.CustomLabels = [0.0, 0.02, 0.04, 0.06]

  # Properties modified on particleDensityLUT
  particleDensityLUT.Annotations = ['0', '0', '0.02', '0.02', '0.04', '0.04', '0.06', '0.06']

  # get layout
  layout1 = GetLayout()

  # layout/tab size in pixels
  layout1.SetSize(836, 716)

  # current camera placement for renderView1
  renderView1.InteractionMode = '2D'
  renderView1.CameraPosition = [182.82, 182.38, 10000.0]
  renderView1.CameraFocalPoint = [182.82, 182.38, 0.0]
  renderView1.CameraParallelScale = 211.9890761754707
  renderView1.Update()

  # save animation

  sim_folder_short = sim_folder.split("/")[-1:]
  sim_folder_short2 = sim_folder_short[0]
  
  if save_anim:
    print('Animation video is written to: '+folder_save_video+'/'+sim_folder_short2+'.avi')
    SaveAnimation(folder_save_video+'/'+sim_folder_short2+'_CellDensity.avi', renderView1, ImageResolution=[1672, 1432],
        FontScaling='Scale fonts proportionally',
        OverrideColorPalette='WhiteBackground',
        StereoMode='No change',
        TransparentBackground=0,
        FrameRate=7,
        FrameWindow=[0, num_frames - 1], 
        # FFMPEG options
        Compression=1,
        Quality='2')

  #--------------------------------------------

# for visualising Capsaspora simulations on a large domain, [0, 1080] x [0, 1080] um
# with cells coloured in local cell density
def Capsaspora1080_CellDensity(sim_folder,folder_save_video,save_anim):

  full_sim_path = sim_folder+'/'

  #### disable automatic camera reset on 'Show'
  paraview.simple._DisableFirstRenderCameraReset()

  ResetSession()

  # get active view
  renderView1 = GetActiveViewOrCreate('RenderView')

  # Hide orientation axes
  renderView1.OrientationAxesVisibility = 0

  num_frames = len(glob.glob(full_sim_path+'results_from_time_0/results_*.vtu'))
  print('num frames: '+str(num_frames))

  # create a new 'XML Unstructured Grid Reader'
  results_ = XMLUnstructuredGridReader(registrationName='results_*', FileName=natural_sort(glob.glob(full_sim_path+'results_from_time_0/results_*.vtu') ) )
  results_.CellArrayStatus = []
  results_.PointArrayStatus = ['Prolif Cell types', 'Legacy Cell types', 'Process rank', 'fbs']
  results_.TimeArray = 'TimeValue'

  # get animation scene
  animationScene1 = GetAnimationScene()

  # update animation scene based on data timesteps
  animationScene1.UpdateAnimationUsingDataTimeSteps()

  # create a new 'XML Unstructured Grid Reader'
  pde_results_fbs_ = XMLUnstructuredGridReader(registrationName='pde_results_fbs_*', FileName= natural_sort(glob.glob(full_sim_path+'results_from_time_0/pde_results_fbs_*.vtu')))
  pde_results_fbs_.CellArrayStatus = []
  pde_results_fbs_.PointArrayStatus = ['fbs']
  pde_results_fbs_.TimeArray = 'TimeValue'

  # create a new 'Transform'
  transform1 = Transform(registrationName='Transform1', Input=pde_results_fbs_)
  transform1.Transform = 'Transform'
  transform1.TransformAllInputVectors = 1

  # Properties modified on transform1.Transform
  transform1.Transform.Translate = [0.0, 0.0, -100.0]
  transform1.Transform.Rotate = [0.0, 0.0, 0.0]
  transform1.Transform.Scale = [3.0, 3.0, 1.0]

  # show data in view
  transform1Display = Show(transform1, renderView1, 'UnstructuredGridRepresentation')

  # hide data in view
  Hide(pde_results_fbs_, renderView1)

  # update the view to ensure updated data information
  renderView1.Update()

  # set scalar coloring
  ColorBy(transform1Display, ('POINTS', 'fbs'))

  # show color bar/color legend
  transform1Display.SetScalarBarVisibility(renderView1, True)

  # get color transfer function/color map for 'fbs'
  fbsLUT = GetColorTransferFunction('fbs')

  # get opacity transfer function/opacity map for 'fbs'
  fbsPWF = GetOpacityTransferFunction('fbs')

  fbsLUT.AutomaticRescaleRangeMode = 'Never'

  # Rescale transfer function
  fbsLUT.RescaleTransferFunction(0.0, 2.0)

  # Rescale transfer function
  fbsPWF.RescaleTransferFunction(0.0, 2.0)

  # get color legend/bar for fbsLUT in view renderView1
  fbsLUTColorBar = GetScalarBar(fbsLUT, renderView1)

  renderView1.Update()

  # set active source
  SetActiveSource(results_)

  # create a new 'Transform'
  transform2 = Transform(registrationName='Transform2', Input=results_)
  transform2.Transform = 'Transform'
  transform2.TransformAllInputVectors = 1

  # init the 'Transform' selected for 'Transform'
  transform2.Transform.Translate = [0.0, 0.0, 0.0]
  transform2.Transform.Rotate = [0.0, 0.0, 0.0]
  transform2.Transform.Scale = [3.0, 3.0, 1.0]

  # show data in view
  transform2Display = Show(transform2, renderView1, 'UnstructuredGridRepresentation')
 
  # hide data in view
  Hide(results_, renderView1)

  # update the view to ensure updated data information
  renderView1.Update()

  # set scalar coloring
  ColorBy(transform2Display, ('POINTS', 'fbs'))

  # show color bar/color legend
  transform2Display.SetScalarBarVisibility(renderView1, True)

  # change representation type
  transform2Display.SetRepresentationType('Point Gaussian')

  # Properties modified on transform2Display
  transform2Display.GaussianRadius = 3.0
  
  # set active source
  SetActiveSource(transform2)

   # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XTitle = '$\\mu m$'
  renderView1.AxesGrid.YTitle = '$\\mu m$     '
  renderView1.AxesGrid.XTitleColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.YTitleColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.GridColor = [0.0, 0.0, 0.0]

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XLabelColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.YLabelColor = [0.0, 0.0, 0.0]
  renderView1.AxesGrid.XAxisUseCustomLabels = 1
  renderView1.AxesGrid.XAxisLabels = [0.0, 200.0, 400.0, 600.0, 800.0, 1000.0]

  # # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.YAxisUseCustomLabels = 1
  renderView1.AxesGrid.YAxisLabels = [0.0, 200.0, 400.0, 600.0, 800.0, 1000.0]

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.UseCustomBounds = 1
  renderView1.AxesGrid.CustomBounds = [0.0, 1080.0, 0.0, 1080.0, 0.0, 1.0]

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XLabelFontSize = 25
  renderView1.AxesGrid.YLabelFontSize = 25

  # Properties modified on renderView1.AxesGrid
  renderView1.AxesGrid.XTitleFontSize = 25
  renderView1.AxesGrid.YTitleFontSize = 25

  # Rescale transfer function
  fbsLUT.RescaleTransferFunction(0.0, 2.0)

  # Rescale transfer function
  fbsPWF.RescaleTransferFunction(0.0, 2.0)

  # get color legend/bar for fbsLUT in view renderView1
  fbsLUTColorBar = GetScalarBar(fbsLUT, renderView1)

  # change scalar bar placement
  fbsLUTColorBar.WindowLocation = 'Any Location'

  fbsLUTColorBar.Title = 'FBS\n'
  fbsLUTColorBar.TitleJustification = 'Centered'
  fbsLUTColorBar.HorizontalTitle = 1
  fbsLUTColorBar.AutomaticLabelFormat = 0
  fbsLUTColorBar.LabelFormat = '%-#6.1f'
  fbsLUTColorBar.AddRangeLabels = 0
  fbsLUTColorBar.ScalarBarLength = 0.3

  # get color legend/bar for fbsLUT in view renderView1
  fbsLUTColorBar = GetScalarBar(fbsLUT, renderView1)

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.TitleColor = [0.0, 0.0, 0.0]

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.LabelColor = [0.0, 0.0, 0.0]

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.TitleFontSize = 12
  fbsLUTColorBar.LabelFontSize = 10

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.TextPosition = 'Ticks left/bottom, annotations right/top'

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.DrawTickLabels = 0
  fbsLUTColorBar.UseCustomLabels = 1

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.CustomLabels = [0.0, 0.5, 1.0, 1.5, 2.0]

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.Position = [0.88, 0.1]
  fbsLUTColorBar.ScalarBarThickness = 15

  # Properties modified on fbsLUTColorBar
  fbsLUTColorBar.DrawTickMarks = 0

  fbsLUT.IndexedColors = [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
  fbsLUT.IndexedOpacities = [1.0, 1.0, 1.0, 1.0]

  # Properties modified on fbsLUT
  fbsLUT.Annotations = ['0', '0%', '0.5', '2.5%', '1', '5%', '1.5', '7.5%', '2', '10%']

  # create a new 'Annotate Time Filter'
  annotateTimeFilter1 = AnnotateTimeFilter(registrationName='AnnotateTimeFilter1', Input=transform2)
  annotateTimeFilter1.Format = 'Time: {time:f}'
  annotateTimeFilter1.Shift = 0.0
  annotateTimeFilter1.Scale = 1.0

  # Properties modified on annotateTimeFilter1
  annotateTimeFilter1.Format = 'Time: {time:.2f} h'
  annotateTimeFilter1.Scale = 0.06666666

  # show data in view
  annotateTimeFilter1Display = Show(annotateTimeFilter1, renderView1, 'TextSourceRepresentation')

  annotateTimeFilter1Display.WindowLocation = 'Upper Left Corner'
  annotateTimeFilter1Display.Position = [0.05, 0.05]
  annotateTimeFilter1Display.Color = [0.0, 0.0, 0.0]

  # update the view to ensure updated data information
  renderView1.Update()

  # Properties modified on annotateTimeFilter1Display
  annotateTimeFilter1Display.FontSize = 40

  # Compute local cell density and set it as the cell colour 
  # set active source
  SetActiveSource(transform2)

  # get display properties
  transform2Display = GetDisplayProperties(transform2, view=renderView1)

  # create a new 'Programmable Filter'
  programmableFilter1 = ProgrammableFilter(registrationName='ProgrammableFilter1', Input=transform2)

  # Properties modified on programmableFilter1
  programmableFilter1.Script = """
  import numpy as np
  from vtkmodules.numpy_interface import algorithms as algs
  from vtkmodules.util import numpy_support

  # Get input data
  input_data = inputs[0]
  # Extract point coordinates
  points = input_data.Points  

  # Radius for circular neighborhood (Modify as needed)
  circle_radius = 10  # Define the radius around each cell
  circle_area = np.pi * (circle_radius ** 2)  # Area of the circular neighborhood

  # Convert points to a NumPy array
  num_points = points.shape[0]
  density_values = np.zeros(num_points)

  # Compute density for each point
  for i, (x, y, z) in enumerate(points):
      # Count neighboring points within the circle
      neighbor_count = np.sum((points[:, 0] - x) ** 2 + (points[:, 1] - y) ** 2 <= circle_radius ** 2)
      
      # Compute density as number of neighbors per unit area
      density_values[i] = neighbor_count / circle_area

  # Convert NumPy array to VTK and add it to the output
  output = self.GetOutput()
  density_array = numpy_support.numpy_to_vtk(density_values, deep=True)
  density_array.SetName("Particle Density")
  output.GetPointData().AddArray(density_array)"""
  programmableFilter1.RequestInformationScript = ''
  programmableFilter1.RequestUpdateExtentScript = ''
  programmableFilter1.PythonPath = ''

  # show data in view
  programmableFilter1Display = Show(programmableFilter1, renderView1, 'UnstructuredGridRepresentation')
  programmableFilter1Display.OpacityArrayName = ['POINTS', 'Particle Density']

  # hide data in view
  Hide(transform2, renderView1)

  # update the view to ensure updated data information
  renderView1.Update()

  # change representation type
  programmableFilter1Display.SetRepresentationType('Point Gaussian')

  # set scalar coloring
  ColorBy(programmableFilter1Display, ('POINTS', 'Particle Density'))

  # rescale color and/or opacity maps used to include current data range
  programmableFilter1Display.RescaleTransferFunctionToDataRange(True, False)

  # show color bar/color legend
  programmableFilter1Display.SetScalarBarVisibility(renderView1, True)

  # get color transfer function/color map for 'ParticleDensity'
  particleDensityLUT = GetColorTransferFunction('ParticleDensity')

  # get opacity transfer function/opacity map for 'ParticleDensity'
  particleDensityPWF = GetOpacityTransferFunction('ParticleDensity')

  # Properties modified on programmableFilter1Display
  programmableFilter1Display.GaussianRadius = 3.0

  # get color legend/bar for particleDensityLUT in view renderView1
  particleDensityLUTColorBar = GetScalarBar(particleDensityLUT, renderView1)

  # change scalar bar placement
  particleDensityLUTColorBar.WindowLocation = 'Any Location'

  # change scalar bar placement
  particleDensityLUTColorBar.Position = [0.88, 0.53]

  # Rescale transfer function
  particleDensityLUT.RescaleTransferFunction(0.0, 0.06)

  # Properties modified on particleDensityLUTColorBar
  particleDensityLUTColorBar.TextPosition = 'Ticks left/bottom, annotations right/top'
  # particleDensityLUTColorBar.DrawTickMarks = 1
  particleDensityLUTColorBar.Title = 'cell \ndensity\n'
  particleDensityLUTColorBar.ComponentTitle = ''
  particleDensityLUTColorBar.TitleColor = [0.0, 0.0, 0.0]
  particleDensityLUTColorBar.LabelColor = [0.0, 0.0, 0.0]
  particleDensityLUTColorBar.ScalarBarThickness = 15
  particleDensityLUTColorBar.AddRangeLabels = 0
  particleDensityLUTColorBar.ScalarBarLength = 0.3
  particleDensityLUTColorBar.TitleJustification = 'Left'

  # Properties modified on particleDensityLUT
  particleDensityLUT.RGBPoints = [0.0, 0.0, 0.0, 0.0, 0.02, 0.647, 0.019, 0.988, 0.04, 0.635, 0.788, 0.0, 0.05, 1.0, 1.0, 0.0, 0.06, 1.0, 1.0, 0.0,]

  # Properties modified on particleDensityLUTColorBar
  particleDensityLUTColorBar.HorizontalTitle = 1

  # Properties modified on particleDensityLUTColorBar
  particleDensityLUTColorBar.TitleFontSize = 12
  particleDensityLUTColorBar.LabelFontSize = 10
  particleDensityLUTColorBar.RangeLabelFormat = '%-#6.2f'

  # Properties modified on fbsLUTColorBar
  particleDensityLUTColorBar.DrawTickLabels = 0
  particleDensityLUTColorBar.DrawTickMarks = 0
  particleDensityLUTColorBar.UseCustomLabels = 1
  particleDensityLUTColorBar.CustomLabels = [0.0, 0.02, 0.04, 0.06]

  # Properties modified on particleDensityLUT
  particleDensityLUT.Annotations = ['0', '0', '0.02', '0.02', '0.04', '0.04', '0.06', '0.06']

  # get layout
  layout1 = GetLayout()

  # layout/tab size in pixels
  layout1.SetSize(836, 716)

  # current camera placement for renderView1
  renderView1.InteractionMode = '2D'
  renderView1.CameraPosition = [547, 540, 10000.0]
  renderView1.CameraFocalPoint = [547, 540, 0.0]
  renderView1.CameraParallelScale = 625
  renderView1.Update()

  # save animation

  sim_folder_short = sim_folder.split("/")[-1:]
  sim_folder_short2 = sim_folder_short[0]
  
  if save_anim:
    print('Animation video is written to: '+folder_save_video+'/'+sim_folder_short2+'.avi')
    SaveAnimation(folder_save_video+'/'+sim_folder_short2+'_CellDensity.avi', renderView1, ImageResolution=[1672, 1432],
        FontScaling='Scale fonts proportionally',
        OverrideColorPalette='WhiteBackground',
        StereoMode='No change',
        TransparentBackground=0,
        FrameRate=7,
        FrameWindow=[0, num_frames - 1], 
        # FFMPEG options
        Compression=1,
        Quality='2')

  #--------------------------------------------

