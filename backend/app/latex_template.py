r"""Fixed LaTeX resume template ("Jake's Resume" style) + macro guide.

The look lives here (code-owned, consistent). The LLM only writes the tailored
*body* using the macros described in MACRO_GUIDE; routes_latex wraps it with
PREAMBLE / CLOSING. This separation keeps the design stable regardless of what
the model returns.
"""

PREAMBLE = r"""\documentclass[letterpaper,10pt]{article}

\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{fontawesome5}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\addtolength{\oddsidemargin}{-0.6in}
\addtolength{\evensidemargin}{-0.6in}
\addtolength{\textwidth}{1.2in}
\addtolength{\topmargin}{-.8in}
\addtolength{\textheight}{1.5in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-6pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-6pt}]

\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}[itemsep=1pt, topsep=2pt, parsep=0pt, partopsep=0pt]}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-6pt}}

\begin{document}
"""

CLOSING = r"""
\end{document}
"""

# Shown to the model so it uses the right macros. Mirrors the source resume's
# structure (header, education, skills, projects, achievements, experience).
MACRO_GUIDE = r"""
HEADER (first thing in the body; fill the candidate's REAL contact info):
\begin{center}
    \textbf{\Huge \scshape FULL NAME} \\ \vspace{1pt}
    \small \faPhone* PHONE $|$ \href{mailto:EMAIL}{\faEnvelope\ EMAIL} $|$
    \href{LINKEDIN_URL}{\faLinkedin\ linkedin-handle} $|$
    \href{GITHUB_URL}{\faGithub\ github-handle}
\end{center}

A SECTION: \section{Section Title}

EDUCATION or EXPERIENCE-with-employer entries:
\resumeSubHeadingListStart
  \resumeSubheading{Institution or Company}{Date or score (right)}{Degree or Role}{Second line (right)}
  \resumeItemListStart
    \resumeItem{Tailored bullet.}
  \resumeItemListEnd
\resumeSubHeadingListEnd

PROJECT entries:
\resumeSubHeadingListStart
  \resumeProjectHeading{\textbf{Project Name} $|$ \emph{Tech, Stack}}{\href{URL}{Live} $|$ \href{URL}{GitHub}}
  \resumeItemListStart
    \resumeItem{Tailored bullet.}
  \resumeItemListEnd
\resumeSubHeadingListEnd
IMPORTANT: \resumeProjectHeading takes EXACTLY TWO {} groups. Put the project name
AND its tech stack TOGETHER in the first group; put the links in the second group.
CORRECT:   \resumeProjectHeading{\textbf{LostNFound} $|$ \emph{Next.js, Prisma}}{\href{U}{Live} $|$ \href{U}{GitHub}}
WRONG:     \resumeProjectHeading{\textbf{LostNFound}}{$|$ \emph{Next.js}}{\href{U}{GitHub}}  (three groups)

PLAIN BULLET sections (Technical Skills, Achievements, Experience) — these show real bullets:
\resumeItemListStart
  \resumeItem{\textbf{Tech Stack}: ...}
  \resumeItem{Another bullet.}
\resumeItemListEnd
"""
