'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { getSupabaseClient } from '@/lib/supabase/client';

interface Job {
    id: string;
    twin_id: string | null;
    source_id: string | null;
    status: string;
    job_type: string;
    priority: number;
    error_message: string | null;
    metadata: Record<string, unknown>;
    created_at: string;
    updated_at: string;
    started_at: string | null;
    completed_at: string | null;
}

interface JobLog {
    id: string;
    job_id: string;
    log_level: string;
    message: string;
    metadata: Record<string, unknown>;
    created_at: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export default function JobDetailPage() {
    const params = useParams();
    const jobId = params.id as string;

    const [job, setJob] = useState<Job | null>(null);
    const [logs, setLogs] = useState<JobLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchJobDetails = useCallback(async () => {
        try {
            setLoading(true);
            const supabase = getSupabaseClient();
            const { data: { session } } = await supabase.auth.getSession();

            if (!session) {
                setError('Not authenticated');
                return;
            }

            // Fetch job details
            const jobResponse = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
                headers: {
                    'Authorization': `Bearer ${session.access_token}`
                }
            });

            if (!jobResponse.ok) {
                throw new Error('Failed to fetch job details');
            }

            const jobData = await jobResponse.json();
            setJob(jobData);

            // Fetch job logs
            const logsResponse = await fetch(`${API_BASE_URL}/jobs/${jobId}/logs`, {
                headers: {
                    'Authorization': `Bearer ${session.access_token}`
                }
            });

            if (logsResponse.ok) {
                const logsData = await logsResponse.json();
                setLogs(logsData);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    }, [jobId]);

    useEffect(() => {
        if (jobId) {
            fetchJobDetails();
        }
    }, [jobId, fetchJobDetails]);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'complete': return 'bg-green-100 text-green-800';
            case 'processing': return 'bg-blue-100 text-blue-800';
            case 'queued': return 'bg-gray-100 text-gray-800';
            case 'failed': return 'bg-red-100 text-red-800';
            case 'needs_attention': return 'bg-yellow-100 text-yellow-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const getLogLevelColor = (level: string) => {
        switch (level) {
            case 'error': return 'text-red-600';
            case 'warning': return 'text-yellow-600';
            case 'info': return 'text-blue-600';
            default: return 'text-gray-600';
        }
    };

    const formatDate = (dateString: string | null) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleString();
    };

    if (loading) {
        return (
            <div className="p-6">
                <div className="animate-pulse">
                    <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
                    <div className="h-48 bg-gray-200 rounded mb-4"></div>
                    <div className="h-64 bg-gray-200 rounded"></div>
                </div>
            </div>
        );
    }

    if (error || !job) {
        return (
            <div className="p-6">
                <Link href="/dashboard/jobs" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
                    ← Back to Jobs
                </Link>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800">{error || 'Job not found'}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <Link href="/dashboard/jobs" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
                ← Back to Jobs
            </Link>

            {/* Job Details Card */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h1 className="text-2xl font-bold mb-2">Job Details</h1>
                        <p className="text-gray-500 text-sm font-mono">{job.id}</p>
                    </div>
                    <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(job.status)}`}>
                        {job.status}
                    </span>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-6">
                    <div>
                        <p className="text-sm text-gray-500">Type</p>
                        <p className="font-medium">{job.job_type}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Priority</p>
                        <p className="font-medium">{job.priority}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Created</p>
                        <p className="font-medium">{formatDate(job.created_at)}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Updated</p>
                        <p className="font-medium">{formatDate(job.updated_at)}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Started</p>
                        <p className="font-medium">{formatDate(job.started_at)}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Completed</p>
                        <p className="font-medium">{formatDate(job.completed_at)}</p>
                    </div>
                </div>

                {job.error_message && (
                    <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <p className="text-sm text-gray-500 mb-1">Error Message</p>
                        <p className="text-red-800">{job.error_message}</p>
                    </div>
                )}

                {Object.keys(job.metadata).length > 0 && (
                    <div className="mt-4">
                        <p className="text-sm text-gray-500 mb-2">Metadata</p>
                        <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-auto">
                            {JSON.stringify(job.metadata, null, 2)}
                        </pre>
                    </div>
                )}
            </div>

            {/* Logs Section */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold">Logs</h2>
                    <button
                        onClick={fetchJobDetails}
                        className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
                    >
                        Refresh
                    </button>
                </div>

                {logs.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">No logs yet</p>
                ) : (
                    <div className="space-y-2">
                        {logs.map((log) => (
                            <div
                                key={log.id}
                                className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg"
                            >
                                <span className={`text-xs font-medium uppercase ${getLogLevelColor(log.log_level)}`}>
                                    [{log.log_level}]
                                </span>
                                <div className="flex-1">
                                    <p className="text-sm">{log.message}</p>
                                    <p className="text-xs text-gray-400 mt-1">
                                        {formatDate(log.created_at)}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
