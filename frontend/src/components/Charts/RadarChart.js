import React, { useRef, useEffect } from 'react';

const RadarChart = ({ data, width = 400, height = 400, className = '' }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!data || !data.labels || !data.datasets) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 40;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw background grid
    drawGrid(ctx, centerX, centerY, radius, data.labels.length);

    // Draw labels
    drawLabels(ctx, centerX, centerY, radius, data.labels);

    // Draw datasets
    data.datasets.forEach((dataset, index) => {
      drawDataset(ctx, centerX, centerY, radius, dataset, data.labels.length);
    });

    // Draw legend
    drawLegend(ctx, data.datasets, width, height);

  }, [data, width, height]);

  const drawGrid = (ctx, centerX, centerY, radius, numPoints) => {
    ctx.strokeStyle = '#374151'; // dark-700
    ctx.lineWidth = 1;

    // Draw concentric circles
    for (let i = 1; i <= 5; i++) {
      ctx.beginPath();
      ctx.arc(centerX, centerY, (radius * i) / 5, 0, 2 * Math.PI);
      ctx.stroke();
    }

    // Draw radial lines
    for (let i = 0; i < numPoints; i++) {
      const angle = (i * 2 * Math.PI) / numPoints - Math.PI / 2;
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(
        centerX + radius * Math.cos(angle),
        centerY + radius * Math.sin(angle)
      );
      ctx.stroke();
    }
  };

  const drawLabels = (ctx, centerX, centerY, radius, labels) => {
    ctx.fillStyle = '#D1D5DB'; // dark-300
    ctx.font = '12px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    labels.forEach((label, index) => {
      const angle = (index * 2 * Math.PI) / labels.length - Math.PI / 2;
      const labelRadius = radius + 20;
      const x = centerX + labelRadius * Math.cos(angle);
      const y = centerY + labelRadius * Math.sin(angle);

      // Adjust text alignment based on position
      if (Math.abs(angle) < Math.PI / 4 || Math.abs(angle - Math.PI) < Math.PI / 4) {
        ctx.textAlign = 'center';
      } else if (angle > 0) {
        ctx.textAlign = 'left';
      } else {
        ctx.textAlign = 'right';
      }

      ctx.fillText(label, x, y);
    });
  };

  const drawDataset = (ctx, centerX, centerY, radius, dataset, numPoints) => {
    if (!dataset.data || dataset.data.length === 0) return;

    const points = dataset.data.map((value, index) => {
      const angle = (index * 2 * Math.PI) / numPoints - Math.PI / 2;
      const normalizedValue = Math.max(0, Math.min(100, value)) / 100;
      const pointRadius = radius * normalizedValue;
      return {
        x: centerX + pointRadius * Math.cos(angle),
        y: centerY + pointRadius * Math.sin(angle)
      };
    });

    // Draw filled area
    ctx.fillStyle = dataset.backgroundColor || 'rgba(59, 130, 246, 0.2)';
    ctx.beginPath();
    points.forEach((point, index) => {
      if (index === 0) {
        ctx.moveTo(point.x, point.y);
      } else {
        ctx.lineTo(point.x, point.y);
      }
    });
    ctx.closePath();
    ctx.fill();

    // Draw border
    ctx.strokeStyle = dataset.borderColor || '#3B82F6';
    ctx.lineWidth = 2;
    ctx.beginPath();
    points.forEach((point, index) => {
      if (index === 0) {
        ctx.moveTo(point.x, point.y);
      } else {
        ctx.lineTo(point.x, point.y);
      }
    });
    ctx.closePath();
    ctx.stroke();

    // Draw points
    ctx.fillStyle = dataset.borderColor || '#3B82F6';
    points.forEach(point => {
      ctx.beginPath();
      ctx.arc(point.x, point.y, 3, 0, 2 * Math.PI);
      ctx.fill();
    });
  };

  const drawLegend = (ctx, datasets, width, height) => {
    const legendY = height - 30;
    const legendItemWidth = 120;
    const startX = (width - (datasets.length * legendItemWidth)) / 2;

    ctx.font = '12px Inter, sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';

    datasets.forEach((dataset, index) => {
      const x = startX + index * legendItemWidth;
      
      // Draw color box
      ctx.fillStyle = dataset.borderColor || '#3B82F6';
      ctx.fillRect(x, legendY - 6, 12, 12);
      
      // Draw label
      ctx.fillStyle = '#F3F4F6'; // dark-100
      ctx.fillText(dataset.label || `Dataset ${index + 1}`, x + 18, legendY);
    });
  };

  return (
    <div className={`flex justify-center ${className}`}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="max-w-full h-auto"
      />
    </div>
  );
};

export default RadarChart;
