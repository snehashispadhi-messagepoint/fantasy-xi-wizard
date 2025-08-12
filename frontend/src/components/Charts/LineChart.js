import React, { useRef, useEffect } from 'react';

const LineChart = ({ data, width = 600, height = 300, className = '' }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!data || !data.labels || !data.datasets) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Chart dimensions
    const padding = 60;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;
    const chartLeft = padding;
    const chartTop = padding;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Find min and max values for scaling
    const allValues = data.datasets.flatMap(dataset => dataset.data);
    const minValue = Math.min(...allValues, 0);
    const maxValue = Math.max(...allValues);
    const valueRange = maxValue - minValue || 1;

    // Draw background
    ctx.fillStyle = '#111827'; // dark-900
    ctx.fillRect(0, 0, width, height);

    // Draw grid
    drawGrid(ctx, chartLeft, chartTop, chartWidth, chartHeight, data.labels, minValue, maxValue);

    // Draw axes
    drawAxes(ctx, chartLeft, chartTop, chartWidth, chartHeight, data.labels, minValue, maxValue);

    // Draw datasets
    data.datasets.forEach((dataset, index) => {
      drawLine(ctx, chartLeft, chartTop, chartWidth, chartHeight, dataset, data.labels, minValue, valueRange);
    });

    // Draw legend
    drawLegend(ctx, data.datasets, width, height);

  }, [data, width, height]);

  const drawGrid = (ctx, left, top, chartWidth, chartHeight, labels, minValue, maxValue) => {
    ctx.strokeStyle = '#374151'; // dark-700
    ctx.lineWidth = 1;

    // Horizontal grid lines
    for (let i = 0; i <= 5; i++) {
      const y = top + (chartHeight * i) / 5;
      ctx.beginPath();
      ctx.moveTo(left, y);
      ctx.lineTo(left + chartWidth, y);
      ctx.stroke();
    }

    // Vertical grid lines
    const stepX = chartWidth / (labels.length - 1);
    for (let i = 0; i < labels.length; i++) {
      const x = left + i * stepX;
      ctx.beginPath();
      ctx.moveTo(x, top);
      ctx.lineTo(x, top + chartHeight);
      ctx.stroke();
    }
  };

  const drawAxes = (ctx, left, top, chartWidth, chartHeight, labels, minValue, maxValue) => {
    ctx.strokeStyle = '#6B7280'; // dark-500
    ctx.lineWidth = 2;

    // X-axis
    ctx.beginPath();
    ctx.moveTo(left, top + chartHeight);
    ctx.lineTo(left + chartWidth, top + chartHeight);
    ctx.stroke();

    // Y-axis
    ctx.beginPath();
    ctx.moveTo(left, top);
    ctx.lineTo(left, top + chartHeight);
    ctx.stroke();

    // X-axis labels
    ctx.fillStyle = '#D1D5DB'; // dark-300
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';

    const stepX = chartWidth / (labels.length - 1);
    labels.forEach((label, index) => {
      const x = left + index * stepX;
      ctx.fillText(label, x, top + chartHeight + 10);
    });

    // Y-axis labels
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';

    for (let i = 0; i <= 5; i++) {
      const value = maxValue - (i * (maxValue - minValue)) / 5;
      const y = top + (chartHeight * i) / 5;
      ctx.fillText(value.toFixed(1), left - 10, y);
    }
  };

  const drawLine = (ctx, left, top, chartWidth, chartHeight, dataset, labels, minValue, valueRange) => {
    if (!dataset.data || dataset.data.length === 0) return;

    const stepX = chartWidth / (labels.length - 1);
    const points = dataset.data.map((value, index) => ({
      x: left + index * stepX,
      y: top + chartHeight - ((value - minValue) / valueRange) * chartHeight
    }));

    // Draw line
    ctx.strokeStyle = dataset.borderColor || '#3B82F6';
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();
    points.forEach((point, index) => {
      if (index === 0) {
        ctx.moveTo(point.x, point.y);
      } else {
        ctx.lineTo(point.x, point.y);
      }
    });
    ctx.stroke();

    // Draw points
    ctx.fillStyle = dataset.borderColor || '#3B82F6';
    points.forEach(point => {
      ctx.beginPath();
      ctx.arc(point.x, point.y, 4, 0, 2 * Math.PI);
      ctx.fill();
      
      // Add white border to points
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 2;
      ctx.stroke();
    });

    // Draw area under line (optional)
    if (dataset.fill) {
      ctx.fillStyle = dataset.backgroundColor || 'rgba(59, 130, 246, 0.1)';
      ctx.beginPath();
      ctx.moveTo(points[0].x, top + chartHeight);
      points.forEach((point, index) => {
        if (index === 0) {
          ctx.lineTo(point.x, point.y);
        } else {
          ctx.lineTo(point.x, point.y);
        }
      });
      ctx.lineTo(points[points.length - 1].x, top + chartHeight);
      ctx.closePath();
      ctx.fill();
    }
  };

  const drawLegend = (ctx, datasets, width, height) => {
    const legendY = 20;
    const legendItemWidth = 150;
    const startX = (width - (datasets.length * legendItemWidth)) / 2;

    ctx.font = '12px Inter, sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';

    datasets.forEach((dataset, index) => {
      const x = startX + index * legendItemWidth;
      
      // Draw color line
      ctx.strokeStyle = dataset.borderColor || '#3B82F6';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(x, legendY);
      ctx.lineTo(x + 20, legendY);
      ctx.stroke();
      
      // Draw label
      ctx.fillStyle = '#F3F4F6'; // dark-100
      ctx.fillText(dataset.label || `Dataset ${index + 1}`, x + 25, legendY);
    });
  };

  return (
    <div className={`flex justify-center ${className}`}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="max-w-full h-auto bg-dark-900 rounded-lg"
      />
    </div>
  );
};

export default LineChart;
