import vtk
import multiprocessing
import tempfile

import i18n

class SurfaceProcess(multiprocessing.Process):

    def __init__(self, pipe, filename, mode, min_value, max_value,
                 decimate_reduction, smooth_relaxation_factor,
                 smooth_iterations, language):

        multiprocessing.Process.__init__(self)
        self.pipe = pipe
        self.filename = filename
        self.mode = mode
        self.min_value = min_value
        self.max_value = max_value
        self.decimate_reduction = decimate_reduction
        self.smooth_relaxation_factor = smooth_relaxation_factor
        self.smooth_iterations = smooth_iterations
        _ = i18n.InstallLanguage(language)


    def run(self):
        self.CreateSurface()

    def SendProgress(self, obj, msg):
        prog = obj.GetProgress()
        self.pipe.send([prog, msg])

    def CreateSurface(self):

        reader = vtk.vtkXMLImageDataReader()
        reader.SetFileName(self.filename)
        reader.Update()

        # Flip original vtkImageData
        flip = vtk.vtkImageFlip()
        flip.SetInput(reader.GetOutput())
        flip.SetFilteredAxis(1)
        flip.FlipAboutOriginOn()

        # Create vtkPolyData from vtkImageData
        if self.mode == "CONTOUR":
            contour = vtk.vtkContourFilter()
            contour.SetInput(flip.GetOutput())
            contour.SetValue(0, self.min_value) # initial threshold
            contour.SetValue(1, self.max_value) # final threshold
            contour.GetOutput().ReleaseDataFlagOn()
            contour.AddObserver("ProgressEvent", lambda obj,evt:
                    self.SendProgress(obj, _("Generating 3D surface...")))
            polydata = contour.GetOutput()
        else: #mode == "GRAYSCALE":
            mcubes = vtk.vtkMarchingCubes()
            mcubes.SetInput(flip.GetOutput())
            mcubes.SetValue(0, 255)
            mcubes.ComputeScalarsOn()
            mcubes.ComputeGradientsOn()
            mcubes.ComputeNormalsOn()
            mcubes.ThresholdBetween(self.min_value, self.max_value)
            mcubes.GetOutput().ReleaseDataFlagOn()
            mcubes.AddObserver("ProgressEvent", lambda obj,evt:
                    self.SendProgress(obj, _("Generating 3D surface...")))
            polydata = mcubes.GetOutput()

        if self.decimate_reduction:
            decimation = vtk.vtkQuadricDecimation()
            decimation.SetInput(polydata)
            decimation.SetTargetReduction(self.decimate_reduction)
            decimation.GetOutput().ReleaseDataFlagOn()
            decimation.AddObserver("ProgressEvent", lambda obj,evt:
                    self.SendProgress(obj, _("Generating 3D surface...")))
            polydata = decimation.GetOutput()

        if self.smooth_iterations and self.smooth_relaxation_factor:
            smoother = vtk.vtkSmoothPolyDataFilter()
            smoother.SetInput(polydata)
            smoother.SetNumberOfIterations(self.smooth_iterations)
            smoother.SetFeatureAngle(80)
            smoother.SetRelaxationFactor(self.smooth_relaxation_factor)
            smoother.FeatureEdgeSmoothingOn()
            smoother.BoundarySmoothingOn()
            smoother.GetOutput().ReleaseDataFlagOn()
            smoother.AddObserver("ProgressEvent", lambda obj,evt:
                    self.SendProgress(obj, _("Generating 3D surface...")))
            polydata = smoother.GetOutput()

        # Filter used to detect and fill holes. Only fill boundary edges holes.
        #TODO: Hey! This piece of code is the same from
        # polydata_utils.FillSurfaceHole, we need to review this.
        filled_polydata = vtk.vtkFillHolesFilter()
        filled_polydata.SetInput(polydata)
        filled_polydata.SetHoleSize(500)
        filled_polydata.AddObserver("ProgressEvent", lambda obj,evt:
                self.SendProgress(obj, _("Generating 3D surface...")))
        polydata = filled_polydata.GetOutput()


        filename = tempfile.mktemp()
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetInput(polydata)
        writer.SetFileName(filename)
        writer.Write()

        self.pipe.send(None)
        self.pipe.send(filename)