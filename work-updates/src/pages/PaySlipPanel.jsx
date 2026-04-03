import React, { useState } from 'react';
import Layout from '../components/Layout';
import { FileText, Search, Download, Plus, Filter, Mail } from 'lucide-react';
import { useProjectFilter } from '../context/ProjectFilterContext';

const PaySlipPanel = () => {
    const { selectedProjectId } = useProjectFilter();
    const [searchQuery, setSearchQuery] = useState('');

    const payslips = [
        { id: 1, employeeName: 'Muralidhar', employeeId: 'EMP001', month: 'March 2026', amount: '₹75,000', status: 'Generated', date: '2026-03-15' },
        { id: 2, employeeName: 'Naveen Kumar', employeeId: 'EMP002', month: 'March 2026', amount: '₹65,000', status: 'Sent', date: '2026-03-16' },
        { id: 3, employeeName: 'Suresh Varma', employeeId: 'EMP003', month: 'March 2026', amount: '₹85,000', status: 'Draft', date: '2026-03-17' },
    ];

    const filteredPayslips = payslips.filter(ps =>
        ps.employeeName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ps.employeeId.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <Layout>
            <div className="mb-8">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Pay Slips Management</h1>
                        <p className="text-slate-500 dark:text-slate-400">Generate and manage employee pay slips globally.</p>
                    </div>
                    <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl font-semibold transition-all shadow-lg shadow-blue-500/20 active:scale-95">
                        <Plus className="h-5 w-5" />
                        Generate New Pay Slip
                    </button>
                </div>
            </div>

            <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200/60 dark:border-slate-800 shadow-sm overflow-hidden">
                <div className="p-4 border-b border-slate-200/60 dark:border-slate-800 flex flex-col md:flex-row gap-4 justify-between bg-slate-50/50 dark:bg-slate-900/20">
                    <div className="relative flex-1 max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                        <input
                            type="text"
                            placeholder="Search by name or ID..."
                            className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <button className="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 flex items-center gap-2">
                            <Filter className="h-4 w-4" /> Filter
                        </button>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-slate-50/50 dark:bg-slate-900/40 text-slate-500 dark:text-slate-400 text-xs uppercase tracking-wider">
                                <th className="px-6 py-4 font-semibold">Employee</th>
                                <th className="px-6 py-4 font-semibold">Month</th>
                                <th className="px-6 py-4 font-semibold">Amount</th>
                                <th className="px-6 py-4 font-semibold">Status</th>
                                <th className="px-6 py-4 font-semibold">Created Date</th>
                                <th className="px-6 py-4 font-semibold text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                            {filteredPayslips.map((ps) => (
                                <tr key={ps.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors group">
                                    <td className="px-6 py-4">
                                        <div>
                                            <p className="font-semibold text-slate-800 dark:text-slate-200">{ps.employeeName}</p>
                                            <p className="text-xs text-slate-500">{ps.employeeId}</p>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">{ps.month}</td>
                                    <td className="px-6 py-4 text-sm font-bold text-slate-800 dark:text-slate-200">{ps.amount}</td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase ${ps.status === 'Sent' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30' :
                                                ps.status === 'Generated' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30' :
                                                    'bg-slate-100 text-slate-700 dark:bg-slate-700'
                                            }`}>
                                            {ps.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-500">{ps.date}</td>
                                    <td className="px-6 py-4 text-right">
                                        <div className="flex justify-end gap-2">
                                            <button title="Email to Employee" className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors">
                                                <Mail className="h-4 w-4" />
                                            </button>
                                            <button title="Download PDF" className="p-2 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 rounded-lg transition-colors">
                                                <Download className="h-4 w-4" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {filteredPayslips.length === 0 && (
                    <div className="py-20 text-center">
                        <FileText className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                        <p className="text-slate-500 dark:text-slate-400">No pay slips found matching your search.</p>
                    </div>
                )}
            </div>
        </Layout>
    );
};

export default PaySlipPanel;
