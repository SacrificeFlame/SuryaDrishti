'use client';

import { useEffect, useRef } from 'react';

interface CloudMovementMapProps {
  cloudData: {
    cloud_map: number[][];
    motion_vectors: Array<Array<{ x: number; y: number }>>;
  };
  location: { lat: number; lon: number };
}

export default function CloudMovementMap({ cloudData, location }: CloudMovementMapProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || !cloudData) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw cloud map
    const cellWidth = canvas.width / cloudData.cloud_map[0].length;
    const cellHeight = canvas.height / cloudData.cloud_map.length;

    cloudData.cloud_map.forEach((row, i) => {
      row.forEach((cell, j) => {
        const x = j * cellWidth;
        const y = i * cellHeight;

        // Color based on cloud type
        if (cell === 0) {
          ctx.fillStyle = 'rgba(135, 206, 235, 0.2)'; // Clear sky - light blue
        } else if (cell === 1) {
          ctx.fillStyle = 'rgba(200, 200, 200, 0.5)'; // Thin cloud - light gray
        } else if (cell === 2) {
          ctx.fillStyle = 'rgba(128, 128, 128, 0.7)'; // Thick cloud - gray
        } else {
          ctx.fillStyle = 'rgba(64, 64, 64, 0.9)'; // Storm - dark gray
        }

        ctx.fillRect(x, y, cellWidth, cellHeight);
      });
    });

    // Draw motion vectors
    const vectorCellWidth = canvas.width / cloudData.motion_vectors[0].length;
    const vectorCellHeight = canvas.height / cloudData.motion_vectors.length;
    const arrowScale = 300;

    ctx.strokeStyle = 'rgba(255, 0, 0, 0.7)';
    ctx.fillStyle = 'rgba(255, 0, 0, 0.7)';
    ctx.lineWidth = 2;

    cloudData.motion_vectors.forEach((row, i) => {
      row.forEach((vector, j) => {
        const startX = (j + 0.5) * vectorCellWidth;
        const startY = (i + 0.5) * vectorCellHeight;
        const endX = startX + vector.x * arrowScale;
        const endY = startY + vector.y * arrowScale;

        // Draw arrow line
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();

        // Draw arrowhead
        const angle = Math.atan2(endY - startY, endX - startX);
        const headLength = 8;
        ctx.beginPath();
        ctx.moveTo(endX, endY);
        ctx.lineTo(
          endX - headLength * Math.cos(angle - Math.PI / 6),
          endY - headLength * Math.sin(angle - Math.PI / 6)
        );
        ctx.lineTo(
          endX - headLength * Math.cos(angle + Math.PI / 6),
          endY - headLength * Math.sin(angle + Math.PI / 6)
        );
        ctx.closePath();
        ctx.fill();
      });
    });

    // Draw microgrid location (center marker)
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Draw safe zone circle
    ctx.strokeStyle = 'rgba(0, 255, 0, 0.5)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(centerX, centerY, 40, 0, 2 * Math.PI);
    ctx.stroke();

    // Draw microgrid marker
    ctx.fillStyle = '#10b981';
    ctx.beginPath();
    ctx.arc(centerX, centerY, 6, 0, 2 * Math.PI);
    ctx.fill();

    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(centerX, centerY, 6, 0, 2 * Math.PI);
    ctx.stroke();

  }, [cloudData]);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-4">Cloud Movement Analysis</h2>
      
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={600}
          height={400}
          className="w-full h-auto border border-gray-200 rounded"
        />
        
        <div className="absolute top-2 right-2 bg-white bg-opacity-90 rounded p-2 text-xs">
          <div className="font-semibold mb-1">Location</div>
          <div>{location.lat.toFixed(4)}°N</div>
          <div>{location.lon.toFixed(4)}°E</div>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-200 border border-gray-300"></div>
          <span>Clear Sky</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-gray-300 border border-gray-300"></div>
          <span>Thin Cloud</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-gray-500 border border-gray-300"></div>
          <span>Thick Cloud</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-gray-700 border border-gray-300"></div>
          <span>Storm</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-1 h-4 bg-red-500"></div>
          <span>Wind Direction</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-green-500 border-2 border-white"></div>
          <span>Microgrid</span>
        </div>
      </div>
    </div>
  );
}

