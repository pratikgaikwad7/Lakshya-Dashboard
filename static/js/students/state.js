const API_URL = '/api/students';
const FILTER_URL = '/api/students/filters';
const BASE_YEAR = 2024; 

let studentsCache = [];
let studentsRequestController = null;
const modal = document.getElementById('studentModal');
const form = document.getElementById('studentForm');
const tableBody = document.getElementById('studentTableBody');
const emptyState = document.getElementById('emptyState');
const modalTitle = document.getElementById('modalTitle');
const CAN_VIEW_EVALUATIONS = document.body.dataset.canViewEvaluations === 'true';
