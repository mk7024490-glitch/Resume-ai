"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  LayoutDashboard,
  Upload,
  FileText,
  Briefcase,
  Settings,
  Search,
  Filter,
  Download,
  Plus,
  Edit,
  Trash2,
  TrendingUp,
  Users,
  Star,
  CheckCircle,
  Clock,
  BarChart3,
} from "lucide-react"

type Page = "dashboard" | "upload" | "evaluations" | "positions" | "settings"

interface JobPosition {
  id: string
  title: string
  department: string
  location: string
  salary: string
  applicants: number
  status: "Active" | "Draft" | "Closed"
  created: string
  description: string
  skills: string[]
}

const mockJobs: JobPosition[] = [
  {
    id: "1",
    title: "Senior Frontend Developer",
    department: "Engineering",
    location: "Remote",
    salary: "$120,000 - $150,000",
    applicants: 24,
    status: "Active",
    created: "Sep 14, 2025",
    description:
      "We're looking for an experienced Frontend Developer to join our growing team. You'll be responsible for building user-facing...",
    skills: ["React", "TypeScript", "Next.js", "Tailwind CSS", "+4 more"],
  },
  {
    id: "2",
    title: "Data Scientist",
    department: "Data & Analytics",
    location: "New York, NY",
    salary: "$100,000 - $130,000",
    applicants: 18,
    status: "Active",
    created: "Sep 16, 2025",
    description:
      "Join our data team to help drive insights and build machine learning models that power our product decisions.",
    skills: ["Python", "Machine Learning", "SQL", "TensorFlow", "+4 more"],
  },
  {
    id: "3",
    title: "UX Designer",
    department: "Design",
    location: "San Francisco, CA",
    salary: "$80,000 - $110,000",
    applicants: 0,
    status: "Draft",
    created: "Sep 18, 2025",
    description:
      "We're seeking a talented UX Designer to create intuitive and engaging user experiences for our products.",
    skills: ["Figma", "Sketch", "Prototyping", "User Research", "+3 more"],
  },
]

export default function ResumeAI() {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard")
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [selectedJobPosition, setSelectedJobPosition] = useState<string>("")
  const [uploadedCount, setUploadedCount] = useState(0)
  const [completedCount, setCompletedCount] = useState(0)
  const [processingCount, setProcessingCount] = useState(0)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    setSelectedFiles(files)
  }

  const handleAnalyzeFiles = () => {
    if (selectedFiles.length > 0 && selectedJobPosition) {
      setProcessingCount(selectedFiles.length)
      // Simulate processing
      setTimeout(() => {
        setUploadedCount(selectedFiles.length)
        setCompletedCount(selectedFiles.length)
        setProcessingCount(0)
      }, 3000)
    }
  }

  const Sidebar = () => (
    <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col h-screen">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-white font-semibold text-lg">ResumeAI</h1>
            <p className="text-gray-400 text-sm">AI-Powered Hiring</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        <button
          onClick={() => setCurrentPage("dashboard")}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
            currentPage === "dashboard" ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-800 hover:text-white"
          }`}
        >
          <LayoutDashboard className="w-5 h-5" />
          Dashboard
        </button>

        <button
          onClick={() => setCurrentPage("upload")}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
            currentPage === "upload" ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-800 hover:text-white"
          }`}
        >
          <Upload className="w-5 h-5" />
          Upload Resume
        </button>

        <button
          onClick={() => setCurrentPage("evaluations")}
          className={`w-full flex items-center justify-between gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
            currentPage === "evaluations"
              ? "bg-blue-600 text-white"
              : "text-gray-300 hover:bg-gray-800 hover:text-white"
          }`}
        >
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5" />
            Evaluations
          </div>
          <Badge className="bg-blue-600 text-white text-xs">24</Badge>
        </button>

        <button
          onClick={() => setCurrentPage("positions")}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
            currentPage === "positions" ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-800 hover:text-white"
          }`}
        >
          <Briefcase className="w-5 h-5" />
          Job Positions
        </button>

        <button
          onClick={() => setCurrentPage("settings")}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
            currentPage === "settings" ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-800 hover:text-white"
          }`}
        >
          <Settings className="w-5 h-5" />
          Settings
        </button>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800 text-gray-400 text-sm">
        <p>© 2024 ResumeAI</p>
        <p>Powered by Advanced AI</p>
      </div>
    </div>
  )

  const DashboardPage = () => (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-gray-400">Welcome back! Here's what's happening with your resume analysis today.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Resumes</p>
                <p className="text-3xl font-bold text-white">0</p>
                <p className="text-green-400 text-sm flex items-center gap-1 mt-1">
                  <TrendingUp className="w-3 h-3" />
                  +12% from last month
                </p>
              </div>
              <FileText className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Daily Evaluations</p>
                <p className="text-3xl font-bold text-white">0</p>
                <p className="text-green-400 text-sm flex items-center gap-1 mt-1">
                  <TrendingUp className="w-3 h-3" />
                  +8% from last month
                </p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Average Score</p>
                <p className="text-3xl font-bold text-white">0%</p>
                <p className="text-green-400 text-sm flex items-center gap-1 mt-1">
                  <TrendingUp className="w-3 h-3" />
                  +3% from last month
                </p>
              </div>
              <Star className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Active Jobs</p>
                <p className="text-3xl font-bold text-white">1</p>
                <p className="text-green-400 text-sm flex items-center gap-1 mt-1">
                  <TrendingUp className="w-3 h-3" />
                  +2 from last month
                </p>
              </div>
              <Briefcase className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Evaluations */}
        <Card className="lg:col-span-2 bg-gray-800 border-gray-700">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-white">Recent Evaluations</CardTitle>
              <CardDescription className="text-gray-400">Latest resume analysis results</CardDescription>
            </div>
            <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
              View All →
            </Button>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <p className="text-gray-400 mb-4">HTTP error! status: 500</p>
              <Button className="bg-blue-600 hover:bg-blue-700">Try Again</Button>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">Quick Actions</CardTitle>
            <CardDescription className="text-gray-400">Common tasks and shortcuts</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              className="w-full bg-blue-600 hover:bg-blue-700 justify-start"
              onClick={() => setCurrentPage("upload")}
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload New Resume
            </Button>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Processing Queue</span>
                <span className="text-white">0/10</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: "0%" }}></div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Storage Used</span>
                <span className="text-white">0.0GB/10GB</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: "0%" }}></div>
              </div>
            </div>

            <div className="pt-4 border-t border-gray-700">
              <h4 className="text-white font-medium mb-2">System Status</h4>
              <div className="flex items-center gap-2 text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-gray-400">Backend connected</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const UploadPage = () => (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Upload Resumes</h1>
        <p className="text-gray-400">Upload candidate resumes for AI-powered analysis and scoring.</p>
      </div>

      {/* Job Position Selection */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Briefcase className="w-5 h-5" />
            Select Job Position
          </CardTitle>
          <CardDescription className="text-gray-400">
            Choose the position you're hiring for to ensure accurate matching.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Select value={selectedJobPosition} onValueChange={setSelectedJobPosition}>
            <SelectTrigger className="bg-gray-900 border-gray-600 text-white">
              <SelectValue placeholder="Select a job position..." />
            </SelectTrigger>
            <SelectContent className="bg-gray-900 border-gray-600">
              {mockJobs.map((job) => (
                <SelectItem key={job.id} value={job.id} className="text-white hover:bg-gray-800">
                  {job.title} - {job.department}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* File Upload */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Upload Files
          </CardTitle>
          <CardDescription className="text-gray-400">
            Drag and drop resume files or click to browse. Supports PDF, DOC, and DOCX files up to 10MB.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed border-gray-600 rounded-lg p-12 text-center">
            {!selectedJobPosition ? (
              <div>
                <Upload className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                <p className="text-gray-400 text-lg mb-2">Select a job position first</p>
                <p className="text-gray-500 text-sm">PDF, DOC, DOCX files up to 10MB each</p>
              </div>
            ) : (
              <div>
                <Upload className="w-12 h-12 text-blue-500 mx-auto mb-4" />
                <Input
                  type="file"
                  multiple
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <p className="text-white text-lg mb-2">Choose files or drag and drop</p>
                  <p className="text-gray-400 text-sm">PDF, DOC, DOCX files up to 10MB each</p>
                </label>
              </div>
            )}
          </div>

          {selectedFiles.length > 0 && (
            <div className="mt-4 space-y-2">
              <p className="text-white font-medium">Selected Files:</p>
              {selectedFiles.map((file, index) => (
                <div key={index} className="flex items-center justify-between bg-gray-900 p-3 rounded-lg">
                  <span className="text-gray-300">{file.name}</span>
                  <span className="text-gray-400 text-sm">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-6">
        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-6 text-center">
            <FileText className="w-8 h-8 text-blue-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-white">{uploadedCount}</p>
            <p className="text-gray-400 text-sm">Total Uploaded</p>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-6 text-center">
            <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-white">{completedCount}</p>
            <p className="text-gray-400 text-sm">Completed</p>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-6 text-center">
            <Clock className="w-8 h-8 text-orange-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-white">{processingCount}</p>
            <p className="text-gray-400 text-sm">Processing</p>
          </CardContent>
        </Card>
      </div>

      {/* Analyze Button */}
      {selectedFiles.length > 0 && selectedJobPosition && (
        <Button onClick={handleAnalyzeFiles} className="w-full bg-blue-600 hover:bg-blue-700 py-3 text-lg">
          <Upload className="w-5 h-5 mr-2" />
          Analyze & Store ({selectedFiles.length} files)
        </Button>
      )}
    </div>
  )

  const EvaluationsPage = () => (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Resume Evaluations</h1>
        <p className="text-gray-400">
          Upload resume files and analyze candidate evaluations with detailed AI-powered scoring.
        </p>
      </div>

      {/* Upload Section */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Upload Resume Files
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-blue-500 mx-auto mb-4" />
            <p className="text-white text-lg mb-2">Upload Resume Files</p>
            <p className="text-gray-400 text-sm mb-6">Backend server required for file upload and analysis.</p>
            <Button className="bg-gray-700 hover:bg-gray-600 text-gray-300">
              <Upload className="w-4 h-4 mr-2" />
              Choose Files
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Analyze Button */}
      <Button className="w-full bg-blue-600 hover:bg-blue-700 py-3" disabled>
        <Upload className="w-5 h-5 mr-2" />
        Analyze & Store (0 files)
      </Button>

      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            placeholder="Search candidates or positions..."
            className="pl-10 bg-gray-800 border-gray-600 text-white placeholder-gray-400"
          />
        </div>
        <Button variant="outline" className="border-gray-600 text-gray-300 hover:bg-gray-800 bg-transparent">
          <Filter className="w-4 h-4 mr-2" />
          All Matches
        </Button>
        <Button variant="outline" className="border-gray-600 text-gray-300 hover:bg-gray-800 bg-transparent">
          <Download className="w-4 h-4 mr-2" />
          Export
        </Button>
      </div>

      {/* Evaluation Results */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Error Loading Evaluations */}
        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-8 text-center">
            <div className="w-12 h-12 bg-red-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-red-400 text-xl">!</span>
            </div>
            <h3 className="text-white text-lg font-medium mb-2">Error Loading Evaluations</h3>
            <p className="text-gray-400 text-sm mb-6">
              Backend server is not running. Please start your Flask backend server.
            </p>
            <div className="flex gap-3 justify-center">
              <Button className="bg-blue-600 hover:bg-blue-700">
                <Clock className="w-4 h-4 mr-2" />
                Try Again
              </Button>
              <Button variant="outline" className="border-gray-600 text-gray-300 hover:bg-gray-800 bg-transparent">
                Check Connection
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Select an Evaluation */}
        <Card className="bg-gray-800 border-gray-700">
          <CardContent className="p-8 text-center">
            <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-gray-400 text-xl">👁</span>
            </div>
            <h3 className="text-white text-lg font-medium mb-2">Select an Evaluation</h3>
            <p className="text-gray-400 text-sm">
              Click on any evaluation to view detailed candidate information and scoring breakdown.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const JobPositionsPage = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Job Positions</h1>
          <p className="text-gray-400">Manage job postings and track applications for your open positions.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="border-gray-600 text-gray-300 hover:bg-gray-800 bg-transparent">
            <Upload className="w-4 h-4 mr-2" />
            Upload JD
          </Button>
          <Button className="bg-blue-600 hover:bg-blue-700">
            <Plus className="w-4 h-4 mr-2" />
            Create Job
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            placeholder="Search jobs or departments..."
            className="pl-10 bg-gray-800 border-gray-600 text-white placeholder-gray-400"
          />
        </div>
        <Select defaultValue="all-departments">
          <SelectTrigger className="w-48 bg-gray-800 border-gray-600 text-white">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-gray-900 border-gray-600">
            <SelectItem value="all-departments" className="text-white">
              All Departments
            </SelectItem>
            <SelectItem value="engineering" className="text-white">
              Engineering
            </SelectItem>
            <SelectItem value="design" className="text-white">
              Design
            </SelectItem>
            <SelectItem value="data" className="text-white">
              Data & Analytics
            </SelectItem>
          </SelectContent>
        </Select>
        <Select defaultValue="all-status">
          <SelectTrigger className="w-32 bg-gray-800 border-gray-600 text-white">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-gray-900 border-gray-600">
            <SelectItem value="all-status" className="text-white">
              All Status
            </SelectItem>
            <SelectItem value="active" className="text-white">
              Active
            </SelectItem>
            <SelectItem value="draft" className="text-white">
              Draft
            </SelectItem>
            <SelectItem value="closed" className="text-white">
              Closed
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Job Cards */}
      <div className="grid gap-6">
        {mockJobs.map((job) => (
          <Card key={job.id} className="bg-gray-800 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold text-white">{job.title}</h3>
                    <Badge
                      className={
                        job.status === "Active"
                          ? "bg-green-900 text-green-300 border-green-700"
                          : job.status === "Draft"
                            ? "bg-yellow-900 text-yellow-300 border-yellow-700"
                            : "bg-gray-700 text-gray-300 border-gray-600"
                      }
                    >
                      {job.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4 text-gray-400 text-sm mb-3">
                    <span className="flex items-center gap-1">
                      <Briefcase className="w-4 h-4" />
                      {job.department}
                    </span>
                    <span>{job.location}</span>
                    <span>{job.salary}</span>
                    <span className="flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      {job.applicants} applicants
                    </span>
                    <span>Created {job.created}</span>
                  </div>
                  <p className="text-gray-300 mb-4">{job.description}</p>
                  <div>
                    <p className="text-gray-400 text-sm mb-2">Required Skills:</p>
                    <div className="flex flex-wrap gap-2">
                      {job.skills.map((skill, index) => (
                        <Badge key={index} variant="outline" className="border-gray-600 text-gray-300">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between pt-4 border-t border-gray-700">
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-gray-600 text-gray-300 hover:bg-gray-700 bg-transparent"
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Edit
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-red-600 text-red-400 hover:bg-red-900 bg-transparent"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )

  const SettingsPage = () => {
    const [hardMatchWeight, setHardMatchWeight] = useState(40)
    const [softMatchWeight, setSoftMatchWeight] = useState(60)
    const [minimumPassingScore, setMinimumPassingScore] = useState(50)
    const [autoApproveThreshold, setAutoApproveThreshold] = useState(85)
    const [maxFileSize, setMaxFileSize] = useState(10)
    const [dataRetention, setDataRetention] = useState(365)

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
            <p className="text-gray-400">Configure your AI resume analysis system and preferences.</p>
          </div>
          <Button className="bg-blue-600 hover:bg-blue-700">
            <CheckCircle className="w-4 h-4 mr-2" />
            Save Changes
          </Button>
        </div>

        {/* AI Configuration */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Settings className="w-5 h-5" />
              AI Configuration
            </CardTitle>
            <CardDescription className="text-gray-400">Adjust how the AI evaluates and scores resumes.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <label className="text-white font-medium">Hard Match Weight: {hardMatchWeight}%</label>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={hardMatchWeight}
                    onChange={(e) => setHardMatchWeight(Number(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                  />
                </div>
                <p className="text-gray-400 text-sm">Weight for exact keyword matches</p>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <label className="text-white font-medium">Soft Match Weight: {softMatchWeight}%</label>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={softMatchWeight}
                    onChange={(e) => setSoftMatchWeight(Number(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                  />
                </div>
                <p className="text-gray-400 text-sm">Weight for semantic understanding</p>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <label className="text-white font-medium">Minimum Passing Score: {minimumPassingScore}%</label>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={minimumPassingScore}
                    onChange={(e) => setMinimumPassingScore(Number(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                  />
                </div>
                <p className="text-gray-400 text-sm">Minimum score to be considered</p>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <label className="text-white font-medium">Auto-Approve Threshold: {autoApproveThreshold}%</label>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={autoApproveThreshold}
                    onChange={(e) => setAutoApproveThreshold(Number(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                  />
                </div>
                <p className="text-gray-400 text-sm">Score for automatic approval</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* File Handling */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Upload className="w-5 h-5" />
              File Handling
            </CardTitle>
            <CardDescription className="text-gray-400">Configure file upload and processing settings.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <label className="text-white font-medium">Maximum File Size (MB)</label>
                <Input
                  type="number"
                  value={maxFileSize}
                  onChange={(e) => setMaxFileSize(Number(e.target.value))}
                  className="bg-gray-900 border-gray-600 text-white"
                />
              </div>

              <div className="space-y-3">
                <label className="text-white font-medium">Data Retention (days)</label>
                <Input
                  type="number"
                  value={dataRetention}
                  onChange={(e) => setDataRetention(Number(e.target.value))}
                  className="bg-gray-900 border-gray-600 text-white"
                />
              </div>
            </div>

            <div className="space-y-3">
              <label className="text-white font-medium">Allowed File Formats</label>
              <div className="flex flex-wrap gap-2">
                <Badge className="bg-blue-600 text-white">PDF</Badge>
                <Badge className="bg-blue-600 text-white">DOC</Badge>
                <Badge className="bg-blue-600 text-white">DOCX</Badge>
                <Badge className="bg-blue-600 text-white">TXT</Badge>
                <Badge className="bg-blue-600 text-white">RTF</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const renderCurrentPage = () => {
    switch (currentPage) {
      case "dashboard":
        return <DashboardPage />
      case "upload":
        return <UploadPage />
      case "evaluations":
        return <EvaluationsPage />
      case "positions":
        return <JobPositionsPage />
      case "settings":
        return <SettingsPage />
      default:
        return <DashboardPage />
    }
  }

  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <div className="p-8">{renderCurrentPage()}</div>
      </main>
    </div>
  )
}
