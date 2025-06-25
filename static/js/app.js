// Глобальная функция для переключения вкладок (объявляем в начале)
function openTab(evt, tabName) {
    console.log('Переключение на вкладку:', tabName);
    
    const tabContents = document.getElementsByClassName('tab-content');
    const tabButtons = document.getElementsByClassName('tab-button');
    
    // Скрыть все вкладки
    for (let content of tabContents) {
        content.classList.remove('active');
    }
    
    // Убрать активный класс с кнопок
    for (let button of tabButtons) {
        button.classList.remove('active');
    }
    
    // Показать выбранную вкладку и активировать кнопку
    const targetTab = document.getElementById(tabName);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    if (evt && evt.currentTarget) {
        evt.currentTarget.classList.add('active');
    }
    
    // Обновить данные при переключении на вкладки
    if (window.app) {
        if (tabName === 'database-tab') {
            window.app.loadDatabaseData();
            window.app.loadDatabaseStats();
        } else if (tabName === 'performance-tab') {
            window.app.loadPerformanceData();
        }
    }
}

// Глобальные функции для отладки
window.getCameraSystemInfo = function() {
    return window.app ? window.app.getSystemInfo() : null;
};

window.exportPerformanceLog = function() {
    if (window.app) {
        window.app.exportPerformanceLog();
    } else {
        console.error('Приложение не инициализировано');
    }
};

window.forceUpdate = function() {
    if (window.app) {
        window.app.updateStatus();
        window.app.loadDatabaseData();
        window.app.loadPerformanceData();
        console.log('Принудительное обновление данных выполнено');
    } else {
        console.error('Приложение не инициализировано');
    }
};

class CameraMonitoringApp {
    constructor() {
        this.isConnected = false;
        this.detectionResults = [];
        this.performanceData = {};
        
        console.log('Инициализация приложения...');
        
        this.initializeElements();
        this.bindEvents();
        this.updateStatus();
        this.loadDatabaseData();
        this.loadDatabaseStats();
        
        // Периодическое обновление статуса (чаще для 25 FPS)
        this.statusInterval = setInterval(() => this.updateStatus(), 3000);
        
        // Автоматическое обновление данных БД
        this.dataRefreshInterval = setInterval(() => {
            if (this.getCurrentTab() === 'database-tab') {
                this.loadDatabaseData();
                this.loadDatabaseStats();
            }
        }, 10000);
        
        // Обновление производительности
        this.performanceInterval = setInterval(() => {
            if (this.getCurrentTab() === 'performance-tab') {
                this.loadPerformanceData();
            }
        }, 5000);
        
        console.log('Приложение инициализировано успешно');
    }
    
    initializeElements() {
        console.log('Инициализация элементов интерфейса...');
        
        this.elements = {
            // Управление
            startButton: document.getElementById('start-camera'),
            stopButton: document.getElementById('stop-camera'),
            restartButton: document.getElementById('restart-camera'),
            refreshButton: document.getElementById('refresh-data'),
            cleanupButton: document.getElementById('cleanup-data'),
            refreshPerformanceButton: document.getElementById('refresh-performance'),
            resetStatsButton: document.getElementById('reset-stats'),
            
            // Статус
            cameraStatus: document.getElementById('camera-status'),
            efficiencyStatus: document.getElementById('efficiency-status'),
            
            // Основные метрики
            framesReceived: document.getElementById('frames-received'),
            framesAnalyzed: document.getElementById('frames-analyzed'),
            currentFps: document.getElementById('current-fps'),
            analysisRate: document.getElementById('analysis-rate'),
            uptime: document.getElementById('uptime'),
            errorCount: document.getElementById('error-count'),
            
            // Производительность
            avgFps: document.getElementById('avg-fps'),
            analysisEfficiency: document.getElementById('analysis-efficiency'),
            framesPerAnalysis: document.getElementById('frames-per-analysis'),
            errorRate: document.getElementById('error-rate'),
            recommendationsList: document.getElementById('recommendations-list'),
            
            // Остальные элементы
            detectionList: document.getElementById('detection-list'),
            databaseTbody: document.getElementById('database-tbody'),
            cameraStats: document.querySelector('.camera-stats'),
            totalRecords: document.getElementById('total-records'),
            dbSize: document.getElementById('db-size'),
            lastActivity: document.getElementById('last-activity')
        };
        
        // Проверяем, какие элементы не найдены
        const missingElements = [];
        for (const [key, element] of Object.entries(this.elements)) {
            if (!element) {
                missingElements.push(key);
            }
        }
        
        if (missingElements.length > 0) {
            console.warn('Не найдены элементы:', missingElements);
        } else {
            console.log('Все элементы интерфейса найдены');
        }
    }
    
    bindEvents() {
        console.log('Привязка событий...');
        
        // Проверяем и привязываем события для кнопок
        if (this.elements.startButton) {
            this.elements.startButton.addEventListener('click', (e) => {
                console.log('Клик по кнопке запуска камеры');
                this.startCamera();
            });
        } else {
            console.error('Кнопка запуска камеры не найдена');
        }
        
        if (this.elements.stopButton) {
            this.elements.stopButton.addEventListener('click', (e) => {
                console.log('Клик по кнопке остановки камеры');
                this.stopCamera();
            });
        } else {
            console.error('Кнопка остановки камеры не найдена');
        }
        
        if (this.elements.restartButton) {
            this.elements.restartButton.addEventListener('click', (e) => {
                console.log('Клик по кнопке перезапуска камеры');
                this.restartCamera();
            });
        } else {
            console.error('Кнопка перезапуска камеры не найдена');
        }
        
        if (this.elements.refreshButton) {
            this.elements.refreshButton.addEventListener('click', (e) => {
                console.log('Клик по кнопке обновления данных');
                this.loadDatabaseData();
            });
        }
        
        if (this.elements.cleanupButton) {
            this.elements.cleanupButton.addEventListener('click', (e) => {
                console.log('Клик по кнопке очистки данных');
                this.cleanupDatabase();
            });
        }
        
        if (this.elements.refreshPerformanceButton) {
            this.elements.refreshPerformanceButton.addEventListener('click', (e) => {
                console.log('Клик по кнопке обновления производительности');
                this.loadPerformanceData();
            });
        }
        
        if (this.elements.resetStatsButton) {
            this.elements.resetStatsButton.addEventListener('click', (e) => {
                console.log('Клик по кнопке сброса статистики');
                this.resetStatistics();
            });
        }
        
        // Обработка видимости страницы
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.reduceUpdateFrequency();
            } else {
                this.restoreUpdateFrequency();
            }
        });
        
        // Обработка закрытия страницы
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
        
        console.log('События привязаны');
    }
    
    cleanup() {
        console.log('Очистка ресурсов...');
        if (this.statusInterval) clearInterval(this.statusInterval);
        if (this.dataRefreshInterval) clearInterval(this.dataRefreshInterval);
        if (this.performanceInterval) clearInterval(this.performanceInterval);
    }
    
    reduceUpdateFrequency() {
        console.log('Снижение частоты обновлений (страница скрыта)');
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
            this.statusInterval = setInterval(() => this.updateStatus(), 15000);
        }
        if (this.performanceInterval) {
            clearInterval(this.performanceInterval);
            this.performanceInterval = setInterval(() => {
                if (this.getCurrentTab() === 'performance-tab') {
                    this.loadPerformanceData();
                }
            }, 30000);
        }
    }
    
    restoreUpdateFrequency() {
        console.log('Восстановление частоты обновлений (страница видима)');
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
            this.statusInterval = setInterval(() => this.updateStatus(), 3000);
        }
        if (this.performanceInterval) {
            clearInterval(this.performanceInterval);
            this.performanceInterval = setInterval(() => {
                if (this.getCurrentTab() === 'performance-tab') {
                    this.loadPerformanceData();
                }
            }, 5000);
        }
        this.updateStatus();
    }
    
    getCurrentTab() {
        const activeTab = document.querySelector('.tab-content.active');
        return activeTab ? activeTab.id : null;
    }
    
    // Управление вкладками (теперь вызывается из глобальной функции)
    openTab(evt, tabName) {
        console.log('Переключение на вкладку через класс:', tabName);
        
        const tabContents = document.getElementsByClassName('tab-content');
        const tabButtons = document.getElementsByClassName('tab-button');
        
        // Скрыть все вкладки
        for (let content of tabContents) {
            content.classList.remove('active');
        }
        
        // Убрать активный класс с кнопок
        for (let button of tabButtons) {
            button.classList.remove('active');
        }
        
        // Показать выбранную вкладку и активировать кнопку
        const targetTab = document.getElementById(tabName);
        if (targetTab) {
            targetTab.classList.add('active');
        }
        
        if (evt && evt.currentTarget) {
            evt.currentTarget.classList.add('active');
        }
        
        // Обновить данные при переключении на вкладки
        if (tabName === 'database-tab') {
            this.loadDatabaseData();
            this.loadDatabaseStats();
        } else if (tabName === 'performance-tab') {
            this.loadPerformanceData();
        }
    }
    
    // Управление камерой
    async startCamera() {
        console.log('Запуск камеры...');
        try {
            this.setButtonState('start', true);
            
            const response = await fetch('/api/camera/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Ответ сервера на запуск камеры:', result);
            
            if (result.success) {
                this.showNotification('Анализ камеры 25 FPS запущен', 'success');
            } else {
                this.showNotification(result.message || 'Неизвестная ошибка', 'error');
            }
        } catch (error) {
            console.error('Ошибка запуска камеры:', error);
            this.showNotification('Ошибка запуска камеры: ' + error.message, 'error');
        } finally {
            this.setButtonState('start', false);
        }
    }
    
    async stopCamera() {
        console.log('Остановка камеры...');
        try {
            this.setButtonState('stop', true);
            
            const response = await fetch('/api/camera/stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Ответ сервера на остановку камеры:', result);
            
            if (result.success) {
                this.showNotification('Анализ камеры остановлен', 'success');
            } else {
                this.showNotification(result.message || 'Неизвестная ошибка', 'error');
            }
        } catch (error) {
            console.error('Ошибка остановки камеры:', error);
            this.showNotification('Ошибка остановки камеры: ' + error.message, 'error');
        } finally {
            this.setButtonState('stop', false);
        }
    }
    
    async restartCamera() {
        console.log('Перезапуск камеры...');
        try {
            this.setButtonState('restart', true);
            
            const response = await fetch('/api/camera/restart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Ответ сервера на перезапуск камеры:', result);
            
            if (result.success) {
                this.showNotification('Камера перезапущена', 'success');
            } else {
                this.showNotification(result.message || 'Неизвестная ошибка', 'error');
            }
        } catch (error) {
            console.error('Ошибка перезапуска камеры:', error);
            this.showNotification('Ошибка перезапуска камеры: ' + error.message, 'error');
        } finally {
            this.setButtonState('restart', false);
        }
    }
    
    async resetStatistics() {
        console.log('Сброс статистики...');
        try {
            const confirmed = confirm('Сбросить статистику нейронной сети?');
            if (!confirmed) return;
            
            this.setButtonState('reset', true);
            
            const response = await fetch('/api/neural/reset-statistics', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Ответ сервера на сброс статистики:', result);
            
            if (result.success) {
                this.showNotification('Статистика сброшена', 'success');
                this.loadPerformanceData();
            } else {
                this.showNotification(result.message || 'Ошибка сброса статистики', 'error');
            }
        } catch (error) {
            console.error('Ошибка сброса статистики:', error);
            this.showNotification('Ошибка сброса статистики: ' + error.message, 'error');
        } finally {
            this.setButtonState('reset', false);
        }
    }
    
    async cleanupDatabase() {
        console.log('Очистка базы данных...');
        try {
            const confirmed = confirm('Удалить записи старше 30 дней? Это действие нельзя отменить.');
            if (!confirmed) return;
            
            this.setButtonState('cleanup', true);
            
            const response = await fetch('/api/database/cleanup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Ответ сервера на очистку БД:', result);
            
            if (result.success) {
                this.showNotification(result.message, 'success');
                this.loadDatabaseData();
                this.loadDatabaseStats();
            } else {
                this.showNotification(result.message || 'Ошибка очистки данных', 'error');
            }
        } catch (error) {
            console.error('Ошибка очистки базы данных:', error);
            this.showNotification('Ошибка очистки базы данных: ' + error.message, 'error');
        } finally {
            this.setButtonState('cleanup', false);
        }
    }
    
    setButtonState(buttonType, disabled) {
        const buttonMap = {
            'start': this.elements.startButton,
            'stop': this.elements.stopButton,
            'restart': this.elements.restartButton,
            'cleanup': this.elements.cleanupButton,
            'reset': this.elements.resetStatsButton
        };
        
        const textMap = {
            'start': { normal: '▶️ Запустить анализ (25 FPS)', loading: '⏳ Запуск...' },
            'stop': { normal: '⏹️ Остановить анализ', loading: '⏳ Остановка...' },
            'restart': { normal: '🔄 Перезапустить', loading: '⏳ Перезапуск...' },
            'cleanup': { normal: '🗑️ Очистить старые данные', loading: '⏳ Очистка...' },
            'reset': { normal: '🔄 Сбросить счетчики', loading: '⏳ Сброс...' }
        };
        
        const button = buttonMap[buttonType];
        const texts = textMap[buttonType];
        
        if (button && texts) {
            button.disabled = disabled;
            button.innerHTML = disabled ? texts.loading : texts.normal;
        }
    }
    
    // Обновление статуса
    async updateStatus() {
        try {
            const response = await fetch('/api/camera/status');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Статус камеры получен:', data);
            
            if (data.success) {
                this.updateCameraStatus(data.camera);
                this.updateNeuralStats(data.neural_network);
                this.updateConfigInfo(data.config);
            }
            
        } catch (error) {
            console.error('Ошибка получения статуса:', error);
        }
    }
    
    updateCameraStatus(cameraData) {
        console.log('Обновление статуса камеры:', cameraData);
        
        // Обновление статуса камеры
        if (this.elements.cameraStatus) {
            const statusText = cameraData.active ? 'Анализ активен' : 'Остановлен';
            const statusClass = cameraData.active ? 'status-active' : 'status-inactive';
            
            this.elements.cameraStatus.innerHTML = `
                <span class="status-indicator ${statusClass}"></span>
                ${statusText}
            `;
        }
        
        // Обновление эффективности
        if (this.elements.efficiencyStatus && cameraData.efficiency !== undefined) {
            this.elements.efficiencyStatus.textContent = `${cameraData.efficiency}%`;
            
            // Цветовая индикация эффективности
            const efficiencyClass = cameraData.efficiency >= 90 ? 'status-active' : 
                                  cameraData.efficiency >= 70 ? 'status-warning' : 'status-inactive';
            this.elements.efficiencyStatus.className = `status-value ${efficiencyClass}`;
        }
        
        // Обновление основных метрик
        if (this.elements.framesReceived) {
            this.elements.framesReceived.textContent = cameraData.frame_count || 0;
        }
        
        if (this.elements.framesAnalyzed) {
            this.elements.framesAnalyzed.textContent = cameraData.analyzed_frame_count || 0;
        }
        
        if (this.elements.currentFps) {
            this.elements.currentFps.textContent = cameraData.current_fps || 0;
        }
        
        if (this.elements.analysisRate) {
            this.elements.analysisRate.textContent = cameraData.analysis_rate || 0;
        }
        
        if (this.elements.uptime) {
            this.elements.uptime.textContent = this.formatUptime(cameraData.uptime || 0);
        }
        
        if (this.elements.errorCount) {
            this.elements.errorCount.textContent = cameraData.error_count || 0;
        }
        
        // Обновление статистики камеры в интерфейсе
        if (this.elements.cameraStats && cameraData.active) {
            const performance = cameraData.performance || {};
            this.elements.cameraStats.innerHTML = `
                <div class="camera-stat">Получено: ${cameraData.frame_count || 0}</div>
                <div class="camera-stat">Проанализировано: ${cameraData.analyzed_frame_count || 0}</div>
                <div class="camera-stat">FPS: ${cameraData.current_fps || 0}/${cameraData.target_fps || 25}</div>
                <div class="camera-stat">Анализ/сек: ${cameraData.analysis_rate || 0}</div>
                <div class="camera-stat">Эффективность: ${cameraData.efficiency || 0}%</div>
                <div class="camera-stat">Ошибки: ${cameraData.error_count || 0}</div>
            `;
        }
    }
    
    updateNeuralStats(neuralData) {
        if (neuralData && neuralData.processed_frames > 0) {
            console.log('Статистика нейронной сети:', neuralData);
        }
    }
    
    updateConfigInfo(configData) {
        if (configData) {
            console.log('Конфигурация системы:', configData);
        }
    }
    
    formatUptime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    // Загрузка данных производительности
    async loadPerformanceData() {
        console.log('Загрузка данных производительности...');
        try {
            this.setRefreshPerformanceButtonState(true);
            
            const response = await fetch('/api/camera/performance');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Данные производительности получены:', result);
            
            if (result.success) {
                this.updatePerformanceDisplay(result.data);
                this.updateRecommendations(result.recommendations || []);
            } else {
                this.showNotification('Ошибка загрузки данных производительности', 'error');
            }
        } catch (error) {
            console.error('Ошибка загрузки данных производительности:', error);
            this.showNotification('Ошибка подключения к API производительности: ' + error.message, 'error');
        } finally {
            this.setRefreshPerformanceButtonState(false);
        }
    }
    
    updatePerformanceDisplay(performanceData) {
        console.log('Обновление отображения производительности:', performanceData);
        
        if (!performanceData) return;
        
        // Обновление метрик производительности
        if (this.elements.avgFps) {
            this.elements.avgFps.textContent = performanceData.average_fps || 0;
            this.setPerformanceIndicator(this.elements.avgFps, performanceData.average_fps, 20, 25);
        }
        
        if (this.elements.analysisEfficiency) {
            const efficiency = performanceData.analysis_efficiency_percent || 0;
            this.elements.analysisEfficiency.textContent = `${efficiency}%`;
            this.setPerformanceIndicator(this.elements.analysisEfficiency, efficiency, 70, 90);
        }
        
        if (this.elements.framesPerAnalysis) {
            this.elements.framesPerAnalysis.textContent = performanceData.frames_per_analysis || 0;
            this.setPerformanceIndicator(this.elements.framesPerAnalysis, performanceData.frames_per_analysis, 30, 25);
        }
        
        if (this.elements.errorRate) {
            const errorRate = performanceData.error_rate_percent || 0;
            this.elements.errorRate.textContent = `${errorRate}%`;
            this.setPerformanceIndicator(this.elements.errorRate, errorRate, 5, 1, true); // true для обратной логики
        }
        
        // Сохранение данных для дальнейшего использования
        this.performanceData = performanceData;
    }
    
    setPerformanceIndicator(element, value, warningThreshold, goodThreshold, reverse = false) {
        // Удаление существующих классов
        element.classList.remove('perf-good', 'perf-warning', 'perf-bad');
        
        let className;
        if (reverse) {
            // Для метрик где меньше = лучше (например, процент ошибок)
            if (value <= goodThreshold) className = 'perf-good';
            else if (value <= warningThreshold) className = 'perf-warning';
            else className = 'perf-bad';
        } else {
            // Для метрик где больше = лучше
            if (value >= goodThreshold) className = 'perf-good';
            else if (value >= warningThreshold) className = 'perf-warning';
            else className = 'perf-bad';
        }
        
        element.classList.add(className);
    }
    
    updateRecommendations(recommendations) {
        console.log('Обновление рекомендаций:', recommendations);
        
        if (!this.elements.recommendationsList) return;
        
        this.elements.recommendationsList.innerHTML = '';
        
        if (!recommendations || recommendations.length === 0) {
            this.elements.recommendationsList.innerHTML = `
                <div class="empty-state">
                    <i>✅</i>
                    <h3>Система работает оптимально</h3>
                    <p>Нет рекомендаций по улучшению производительности</p>
                </div>
            `;
            return;
        }
        
        recommendations.forEach(recommendation => {
            const recommendationDiv = document.createElement('div');
            recommendationDiv.className = 'recommendation-item';
            recommendationDiv.innerHTML = `
                <div class="recommendation-icon">💡</div>
                <div class="recommendation-text">${recommendation}</div>
            `;
            this.elements.recommendationsList.appendChild(recommendationDiv);
        });
    }
    
    setRefreshPerformanceButtonState(loading) {
        const button = this.elements.refreshPerformanceButton;
        if (!button) return;
        
        button.disabled = loading;
        
        if (loading) {
            button.innerHTML = '<span class="spinner"></span> Анализ...';
        } else {
            button.innerHTML = '📈 Обновить статистику';
        }
    }
    
    // Работа с базой данных
    async loadDatabaseData() {
        console.log('Загрузка данных из базы данных...');
        try {
            this.setRefreshButtonState(true);
            
            const response = await fetch('/api/database/results?limit=50');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Данные из БД получены:', result);
            
            if (result.success) {
                this.displayDatabaseData(result.data);
                this.updateDetectionResults(result.data.slice(0, 10));
            } else {
                this.showNotification('Ошибка загрузки данных', 'error');
            }
        } catch (error) {
            console.error('Ошибка загрузки данных из БД:', error);
            this.showNotification('Ошибка подключения к базе данных: ' + error.message, 'error');
        } finally {
            this.setRefreshButtonState(false);
        }
    }
    
    async loadDatabaseStats() {
        console.log('Загрузка статистики базы данных...');
        try {
            const response = await fetch('/api/database/info');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Статистика БД получена:', result);
            
            if (result.success && result.data) {
                const data = result.data;
                
                if (this.elements.totalRecords) {
                    this.elements.totalRecords.textContent = data.results_count || 0;
                }
                
                if (this.elements.dbSize) {
                    this.elements.dbSize.textContent = data.database_size || 'Неизвестно';
                }
                
                if (this.elements.lastActivity && data.last_activity) {
                    const lastActivity = new Date(data.last_activity);
                    this.elements.lastActivity.textContent = lastActivity.toLocaleString('ru-RU');
                }
            }
        } catch (error) {
            console.error('Ошибка загрузки статистики БД:', error);
        }
    }
    
    setRefreshButtonState(loading) {
        const button = this.elements.refreshButton;
        if (!button) return;
        
        button.disabled = loading;
        
        if (loading) {
            button.innerHTML = '<span class="spinner"></span> Загрузка...';
        } else {
            button.innerHTML = '🔄 Обновить данные';
        }
    }
    
    // Утилитарная функция для парсинга detection_results
    parseDetectionResults(detectionResults) {
        console.log('Парсинг detection_results:', typeof detectionResults, detectionResults);
        
        if (!detectionResults) {
            return [];
        }
        
        // Если это уже массив
        if (Array.isArray(detectionResults)) {
            return detectionResults;
        }
        
        // Если это строка JSON
        if (typeof detectionResults === 'string') {
            try {
                const parsed = JSON.parse(detectionResults);
                return Array.isArray(parsed) ? parsed : [];
            } catch (e) {
                console.error('Ошибка парсинга JSON:', e, detectionResults);
                return [];
            }
        }
        
        // Если это объект
        if (typeof detectionResults === 'object') {
            // Возможно, это объект с массивом внутри
            if (detectionResults.results && Array.isArray(detectionResults.results)) {
                return detectionResults.results;
            }
            // Или сам объект нужно превратить в массив
            return [detectionResults];
        }
        
        console.warn('Неизвестный формат detection_results:', detectionResults);
        return [];
    }
    
    displayDatabaseData(data) {
        console.log('Отображение данных БД:', data ? data.length : 0, 'записей');
        
        const tbody = this.elements.databaseTbody;
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (!data || data.length === 0) {
            const row = tbody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 4;
            cell.innerHTML = `
                <div class="empty-state">
                    <i>📊</i>
                    <h3>Нет данных</h3>
                    <p>Результаты анализа будут отображаться здесь</p>
                </div>
            `;
            return;
        }
        
        data.forEach((item, index) => {
            try {
                const row = tbody.insertRow();
                row.className = 'fade-in';
                
                // ID
                const idCell = row.insertCell();
                idCell.textContent = item.id;
                
                // Время
                const timeCell = row.insertCell();
                const date = new Date(item.timestamp);
                timeCell.textContent = date.toLocaleString('ru-RU');
                timeCell.title = `Создано: ${new Date(item.created_at).toLocaleString('ru-RU')}`;
                
                // Обнаруженные объекты
                const objectsCell = row.insertCell();
                
                // Используем утилитарную функцию для парсинга
                const detectionResults = this.parseDetectionResults(item.detection_results);
                console.log(`Запись ${index + 1}: обработано ${detectionResults.length} результатов детекции`);
                
                if (detectionResults && detectionResults.length > 0) {
                    const objectsDiv = document.createElement('div');
                    objectsDiv.className = 'object-list';
                    
                    // Группировка объектов по типу
                    const objectCounts = {};
                    detectionResults.forEach(result => {
                        const type = result.object_type || 'unknown';
                        objectCounts[type] = (objectCounts[type] || 0) + 1;
                    });
                    
                    // Создание тегов для каждого типа объекта
                    Object.entries(objectCounts).forEach(([type, count]) => {
                        const tag = document.createElement('span');
                        tag.className = `object-tag ${type}`;
                        tag.textContent = count > 1 ? `${type} (${count})` : type;
                        objectsDiv.appendChild(tag);
                    });
                    
                    objectsCell.appendChild(objectsDiv);
                } else {
                    objectsCell.innerHTML = '<span style="color: #6c757d;">Нет объектов</span>';
                }
                
                // Количество объектов
                const countCell = row.insertCell();
                const count = detectionResults ? detectionResults.length : 0;
                countCell.innerHTML = `
                    <strong>${count}</strong>
                    ${item.processing_time ? `<br><small>${(item.processing_time * 1000).toFixed(0)}мс</small>` : ''}
                `;
            } catch (error) {
                console.error(`Ошибка обработки записи ${index + 1}:`, error, item);
                
                // Создаем строку с информацией об ошибке
                const row = tbody.insertRow();
                row.className = 'error-row';
                
                const errorCell = row.insertCell();
                errorCell.colSpan = 4;
                errorCell.innerHTML = `
                    <div style="color: #dc3545; padding: 10px;">
                        ❌ Ошибка обработки записи ID: ${item.id || 'неизвестно'}
                        <br><small>${error.message}</small>
                    </div>
                `;
            }
        });
    }
    
    updateDetectionResults(recentData) {
        console.log('Обновление результатов детекции:', recentData ? recentData.length : 0, 'записей');
        
        if (!this.elements.detectionList) return;
        
        if (!recentData || recentData.length === 0) {
            this.elements.detectionList.innerHTML = `
                <div class="empty-state">
                    <i>🔍</i>
                    <h3>Нет результатов детекции</h3>
                    <p>Результаты анализа будут отображаться здесь</p>
                </div>
            `;
            return;
        }
        
        this.elements.detectionList.innerHTML = '';
        
        // Показать только последние результаты с объектами
        const resultsWithObjects = recentData.filter(item => {
            const detectionResults = this.parseDetectionResults(item.detection_results);
            return detectionResults && detectionResults.length > 0;
        }).slice(0, 5);
        
        if (resultsWithObjects.length === 0) {
            this.elements.detectionList.innerHTML = `
                <div class="empty-state">
                    <i>🔍</i>
                    <h3>Нет объектов в последних кадрах</h3>
                    <p>Система анализирует кадры, но объекты не обнаружены</p>
                </div>
            `;
            return;
        }
        
        resultsWithObjects.forEach(item => {
            const detectionResults = this.parseDetectionResults(item.detection_results);
            
            detectionResults.forEach(detection => {
                try {
                    const detectionDiv = document.createElement('div');
                    detectionDiv.className = 'detection-item fade-in';
                    
                    const confidence = detection.confidence || 0;
                    let confidenceClass = 'low';
                    if (confidence > 0.8) confidenceClass = 'high';
                    else if (confidence > 0.6) confidenceClass = 'medium';
                    
                    const objectType = detection.object_type || 'unknown';
                    const bbox = detection.bbox || [];
                    const timestamp = detection.timestamp || item.timestamp;
                    const frameSize = detection.frame_size;
                    
                    detectionDiv.innerHTML = `
                        <div class="detection-item-header">
                            <span class="detection-type">${objectType}</span>
                            <span class="detection-confidence ${confidenceClass}">
                                ${(confidence * 100).toFixed(1)}%
                            </span>
                        </div>
                        <div class="detection-details">
                            <span>Координаты: [${bbox.join(', ')}]</span>
                            <span>Время: ${new Date(timestamp).toLocaleTimeString('ru-RU')}</span>
                            ${frameSize ? `<span>Размер кадра: ${frameSize.join('x')}</span>` : ''}
                        </div>
                    `;
                    
                    this.elements.detectionList.appendChild(detectionDiv);
                } catch (error) {
                    console.error('Ошибка обработки детекции:', error, detection);
                }
            });
        });
    }
    
    // Уведомления
    showNotification(message, type = 'info') {
        console.log('Показать уведомление:', type, message);
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        notification.innerHTML = `
            <span style="margin-right: 10px; font-size: 16px;">${icons[type] || icons.info}</span>
            ${message}
        `;
        
        document.body.appendChild(notification);
        
        // Автоматическое удаление через 5 секунд
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
        
        // Возможность закрытия по клику
        notification.addEventListener('click', () => {
            notification.remove();
        });
    }
    
    // Утилиты для отладки и мониторинга
    getSystemInfo() {
        return {
            performance: this.performanceData,
            updateIntervals: {
                status: this.statusInterval ? 3000 : 'остановлен',
                data: this.dataRefreshInterval ? 10000 : 'остановлен',
                performance: this.performanceInterval ? 5000 : 'остановлен'
            },
            currentTab: this.getCurrentTab(),
            elementsLoaded: Object.keys(this.elements).length,
            timestamp: new Date().toISOString()
        };
    }
    
    // Экспорт данных для отладки
    exportPerformanceLog() {
        const logData = {
            timestamp: new Date().toISOString(),
            systemInfo: this.getSystemInfo(),
            performanceData: this.performanceData,
            userAgent: navigator.userAgent,
            viewportSize: {
                width: window.innerWidth,
                height: window.innerHeight
            }
        };
        
        const dataStr = JSON.stringify(logData, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `camera_monitoring_performance_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        link.click();
        
        this.showNotification('Лог производительности экспортирован', 'success');
    }
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM загружен, инициализация приложения...');
    try {
        window.app = new CameraMonitoringApp();
        console.log('Система мониторинга IP камер (25 FPS) инициализирована');
        console.log('Доступные команды: getCameraSystemInfo(), exportPerformanceLog(), forceUpdate()');
    } catch (error) {
        console.error('Ошибка инициализации приложения:', error);
    }
});

// Обработка глобальных ошибок
window.addEventListener('error', (event) => {
    console.error('Глобальная ошибка:', event.error);
    if (window.app) {
        window.app.showNotification('Произошла ошибка в приложении', 'error');
    }
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Необработанное отклонение промиса:', event.reason);
    if (window.app) {
        window.app.showNotification('Ошибка обработки данных', 'error');
    }
});

// Обработка изменения сетевого статуса
window.addEventListener('online', () => {
    console.log('Соединение с сетью восстановлено');
    if (window.app) {
        window.app.showNotification('Соединение с сетью восстановлено', 'success');
        window.app.updateStatus();
    }
});

window.addEventListener('offline', () => {
    console.log('Соединение с сетью потеряно');
    if (window.app) {
        window.app.showNotification('Соединение с сетью потеряно', 'warning');
    }
});
