%% This  'jofyrep.cls' is modified version of phrep.cls by J. Kaipio 3.7.1995.
%% Modifications are done by M. Kuittinen during years 1998-2000.
%%
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{uefrep}[2011/11/16 Physics Report Class for Thesis and Reports]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{report}}
%\DeclareOption{twoside}{\@twosidetrue  \@mparswitchtrue}
%\DeclareOption{phproof}{\input{phproof.sty}}

% To prepare manuscript for B5 size use this option. Note, final
% ps-file have to be created by dvips with option -x800, which 
% means reduction of size by 80 %

\newcommand{\BFive}{
  \typeout{  ... B5 OK }
  \setlength{\topmargin}{-1cm}
  \setlength{\textwidth}{16cm}
  \setlength{\textheight}{23.75cm}
  \newdimen\dblfigwidth
  \dblfigwidth\textwidth
  \divide\dblfigwidth by 2 
  \advance\dblfigwidth by -2mm
}

\ProcessOptions

%\LoadClass[a4paper,twoside,final,onecolumn]{report}
\LoadClass[a4paper]{report}
%
\RequirePackage{amssymb,eufrak,euscript}
%
\typeout{Defining\space PH\space headings ...}
%
%%% The PH headings (adapted from latex.tex), J. Kaipio, 28.3.1995
%
     \if@twoside         % If two-sided printing.
        \typeout{   ...      twoside OK}
        \def\ps@PHheadings{\let\@mkboth\markboth
        \def\@oddfoot{}\def\@evenfoot{}%       No feet.
        \def\@evenhead{\vbox{%
            \hbox to\textwidth{\rm \thepage\hfil \bf \leftmark}%
            \vspace{3pt}%
            \hbox to\textwidth {\hrulefill}%
                    }}%
        \def\@oddhead{\vbox{%
            \hbox to\textwidth{\hbox{}\bf \rightmark \hfil \rm\thepage}%
            \vspace{3pt}%
            \hbox to\textwidth {\hrulefill}%
                   }}%
        \def\chaptermark##1{\markboth {{\ifnum \c@secnumdepth >\m@ne%
           \thechapter. \ \fi ##1}}{}}%
        \def\sectionmark##1{\markright {{\ifnum \c@secnumdepth >\z@%
           \thesection \ \fi ##1}}%
           }%
     }%
     %
     \else%               % If one-sided printing.
     %
        \typeout{   ...      oneside OK}
        \def\ps@PHheadings{\let\@mkboth\markboth%
        \def\@oddfoot{}\def\@evenfoot{}%     No feet.
        \def\@oddhead{\vbox{%
            \hbox to\textwidth{\hbox{}\bf \rightmark \hfil \rm\thepage}%
            \vspace{3pt}%
            \hbox to\textwidth {\hrulefill}%
                   }}%
         \def\chaptermark##1{\markright {{\ifnum \c@secnumdepth >\m@ne%
         \thechapter. \ \fi ##1}}}}%
     \fi%
%%
%%%%%%%%%%%%%      PAGE LAYOUT, J.K. 29.3.1995        %%%%%%%%%%%%%%%
%%

%% In the \twoside style you have to have
%% \oddsidemargin = \paperwidth - \textwidth - 2in - \evensidemargin
\if@twoside                 % Values for two-sided printing:
   \setlength{\evensidemargin}{59pt}   
   \setlength{\oddsidemargin}{\paperwidth}
   \addtolength{\oddsidemargin}{-\textwidth}
   \addtolength{\oddsidemargin}{-2in}
   \addtolength{\oddsidemargin}{-\evensidemargin}
   \setlength{\marginparwidth}{85pt}    
\else                      
   \setlength{\evensidemargin}{25pt}
   \setlength{\oddsidemargin}{25pt}
   \setlength{\marginparwidth}{68pt}
\fi
\setlength{\marginparsep}{10pt}
\setcounter{secnumdepth}{2}

\typeout{The chapter definitions ...}
 
%%         THE CHAPTER DEFINITIONS FOR \chapter, \chapter* AND \chaptertwo
%%
%% \@makechapterhead {TEXT} : Makes the heading for the \chapter command.
%%
%%  Chapter for UKU Phys. dept.   J. Kaipio 3.10.1990

\renewcommand{\@makechapterhead}[1]{%   Heading for \chapter command
  {\parindent=0pt
   \baselineskip=0pt
   \parskip=0pt
\vbox{
  \hbox to\textwidth {\hrulefill}
  \vbox to 3pt{ }
  \hbox to\textwidth {\hfill{\large\textsc{\@chapapp{}} \ %
  \ifappendix
   \textrm{\Alph{chapter}}
  \else  
   \textrm{\Roman{chapter}}
  \fi
  }}
  \vbox to 3pt{ }
  \hbox to\textwidth {\hrulefill}
  \vbox to 3pt{ }
  \hbox to\textwidth {\hfill{\Large\textbf{#1}}}
  }}\par\vspace{5cm}
  }

%% \@makeschapterhead {TEXT} : Makes the heading for the \chapter* command.
%%

\renewcommand{\@makeschapterhead}[1]{%   Heading for \chapter* command
  {\parindent=0pt
   \baselineskip=0pt
   \parskip=0pt
\vbox{
  \hbox to\textwidth {\hrulefill}
  \vbox to 3pt{ }
  \hbox to\textwidth {\hfill{\large\textsc{#1}}}
  \vbox to 3pt{ }
  \hbox to\textwidth {\hrulefill}
  }}\par\vspace{6cm} 
 }


%% A CHAPTER -macro for two caption lines.
%%                        J. Kaipio  8.4.1992

\newcommand{\@makechapterheadtwo}[2]{%   Heading for \chaptertwo command
  {\parindent=0pt
   \baselineskip=0pt
   \parskip=0pt
\vbox{
  \hbox to\textwidth {\hrulefill}
  \vbox to 3pt{ }
  \hbox to\textwidth {\hfill{\large\textsc{\@chapapp{}} \ %
  \ifappendix 
   \textrm{\Alph{chapter}}
  \else  
   \textrm{\Roman{chapter}}
  \fi        
   }}
  \vbox to 3pt{ }
  \hbox to\textwidth {\hrulefill}
  \vbox to 3pt{ }
  \hbox to\textwidth {\hfill{\Large\textbf{#1}}}
  \vbox to 3pt{ }
  \hbox to\textwidth {\hfill{\Large\textbf{#2}}}
  }}\par\vspace{5cm}
  }
%%
%% Modified CHAPTER -> CHAPTERTWO macros for two caption lines.
%%                          J. Kaipio  8.4.1992

\def\chaptertwo{\clearpage   % Starts new page.
   \thispagestyle{plain}     % Page style of chapter page is 'plain'
   \global\@topnum\z@        % Prevents figures from going at top of page.
   \@afterindentfalse        % Suppresses indent in first paragraph.  Change
   \secdef\@chaptertwo\@schaptertwo}   % to \@afterindenttrue to have indent.

\def\@chaptertwo[#1]#2#3{\ifnum \c@secnumdepth >\m@ne
        \refstepcounter{chapter}
        \typeout{\@chapapp\space\thechapter.}
        \addcontentsline{toc}{chapter}{\protect
        \numberline{\thechapter}#1 #3}\else
      \addcontentsline{toc}{chapter}{#1 #3}\fi
   \chaptermark{#1}
   \addtocontents{lof}{\protect\addvspace{10pt}} % Adds between-chapter space
   \addtocontents{lot}{\protect\addvspace{10pt}} % to lists of figs & tables.
   \if@twocolumn                                 % Tests for two-column mode.
           \@topnewpage[\@makechapterheadtwo{#2}{#3}]
     \else \@makechapterheadtwo{#2}{#3}
           \@afterheading                  % Routine called after chapter and
     \fi}                                  % section heading.

\def\@schaptertwo#1{\if@twocolumn \@topnewpage[\@makeschapterhead{#1}]
        \else \@makeschapterhead{#1}
              \@afterheading\fi}

% END OF CHAPTER DEFINITIONS, J.Kaipio, last modified 4.7.1995

%%
%% Modified CHAPTER -> CHAPTERAPP macros for appendices.
%%                          M. Kuittinen  5.5.1998

\def\chapterapp{\clearpage   % Starts new page.
   \thispagestyle{plain}     % Page style of chapter page is 'plain'
   \global\@topnum\z@        % Prevents figures from going at top of page.
   \@afterindentfalse        % Suppresses indent in first paragraph.  Change
   \secdef\@chapterapp\@schapterapp}   % to \@afterindenttrue to have indent.

\def\@chapterapp[#1]#2{\ifnum \c@secnumdepth >\m@ne
        \refstepcounter{chapter}
        \typeout{\@chapapp\space\thechapter.}
        \addcontentsline{toc}{section}{\protect    %dirty tricks with \bf
        \numberline{\bf\thechapter}\bf#1}\else
      \addcontentsline{toc}{chapter}{#1}\fi
   \chaptermark{#1}
   \addtocontents{lof}{\protect\addvspace{10pt}} % Adds between-chapter space
   \addtocontents{lot}{\protect\addvspace{10pt}} % to lists of figs & tables.
   \if@twocolumn                                 % Tests for two-column mode.
           \@topnewpage[\@makechapterhead{#2}]
     \else \@makechapterhead{#2}
           \@afterheading                  % Routine called after chapter and
     \fi}                                  % section heading.

\def\@schapterapp#1{\if@twocolumn \@topnewpage[\@makeschapterhead{#1}]
        \else \@makeschapterhead{#1}
              \@afterheading\fi}

% END OF CHAPTERAPP DEFINITIONS, M. Kuittinen, last modified 5.5.1998

%%
%% Modified CHAPTERAPP -> CHAPTERAPPTWO macros for appendices with two 
%%            caption lines.
%%                        M. Kuittinen  5.5.1998

\def\chapterapptwo{\clearpage   % Starts new page.
   \thispagestyle{plain}     % Page style of chapter page is 'plain'
   \global\@topnum\z@        % Prevents figures from going at top of page.
   \@afterindentfalse        % Suppresses indent in first paragraph.  Change
   \secdef\@chapterapptwo\@schapterapptwo}   % to \@afterindenttrue to have 
                         % indent.

\def\@chapterapptwo[#1]#2#3{\ifnum \c@secnumdepth >\m@ne
        \refstepcounter{chapter}
        \typeout{\@chapapp\space\thechapter.}
        \addcontentsline{toc}{section}{\protect      %dirty tricks with \bf
        \numberline{\bf\thechapter}\bf#1 #3}\else
        \addcontentsline{toc}{chapter}{#1 #3}\fi
   \chaptermark{#1}
   \addtocontents{lof}{\protect\addvspace{10pt}} % Adds between-chapter space
   \addtocontents{lot}{\protect\addvspace{10pt}} % to lists of figs & tables.
   \if@twocolumn                                 % Tests for two-column mode.
           \@topnewpage[\@makechapterheadtwo{#2}{#3}]
     \else \@makechapterheadtwo{#2}{#3}
           \@afterheading                  % Routine called after chapter and
     \fi}                                  % section heading.

\def\@schapterapptwo#1{\if@twocolumn \@topnewpage[\@makeschapterhead{#1}]
        \else \@makeschapterhead{#1}
              \@afterheading\fi}

%% END OF CHAPTERAPPTWO DEFINITIONS, M. Kuittinen, last modified 5.5.1998

%%%%%%%%%%%%      SECTIONING STYLES      %%%%%%%%%%%%%
%%
% The following dimensions changed by J. Kaipio 10.10.1990
\renewcommand{\section}{%
  \@startsection{section}{1}{\z@}{-2.8ex plus -1ex minus
    -.2ex}{1.6ex plus .2ex}{\large\bf}}
\renewcommand{\subsection}{%
  \@startsection{subsection}{2}{\z@}{-2.0ex plus -1ex minus
   -.2ex}{1.5ex plus .2ex}{\normalsize\bf}}
\renewcommand{\subsubsection}{%
  \@startsection{subsubsection}{3}{\z@}{-2.0ex plus
   -1ex minus -.2ex}{1.5ex plus .2ex}{\normalsize\sc}}
%%
%\renewcommand{\thetable}{\thechapter.\@arabic\c@table}
%\renewcommand{\thechapter}{\Roman{chapter}}
%% A style for a single appendix chapter with several sections
\newcommand{\appendices}{%
  \par
  \setcounter{chapter}{0}
  \setcounter{section}{0}
  \renewcommand{\@chapapp}{\appendixname}
  \appendixtrue \typeout{Appendices defined ...}
  \renewcommand{\thechapter}{\Alph{chapter}}
  \addcontentsline{toc}{chapter}{\enclname}  % M. Kuittinen 14.11.2017 to get correct hyperlinks in the pdf-file
  %\addtocontents{toc}{\protect\contentsline{chapter}{\enclname}{~}{~} % original version of the above line
  % } %\vspace{1pt}
}%

\renewcommand{\appendix}{%
  \par
  \setcounter{chapter}{0}
  \setcounter{section}{0}
  \renewcommand{\@chapapp}{\appendixname}
  \appendixtrue \typeout{Appendix defined ...}
  \renewcommand{\thechapter}{\Alph{chapter}}
  \addcontentsline{toc}{chapter}{\appendixname} % M. Kuittinen 14.11.2017 to get correct hyperlinks in the pdf-file 
  %\addtocontents{toc}{\protect\contentsline{chapter}{\appendixname}{~}{~} % original version of the above line
  %} %\vspace{1pt}
}%
%%%%%%%%     MISCELLANEA           %%%%%%%%%%%%%%%%
%% The LABEL extensions for proofing. J. Kaipio, 4.4.1995
%% Some addings to handle appendices. M. Kuittinen, 30.4.1998

\def\seclabel#1{\label{#1}}
\def\eqnlabel#1{\label{#1}}
%\renewcommand{\bibname}{References}  % \refname ?
\newif\ifappendix
\appendixfalse
\newcommand{\enclname}{Appendices} % If using babel this command does not work!
\newcommand{\prefacename}{Preface}

\newcommand{\extratitle}[1]{%   Heading for extra pages
  \clearpage
  \thispagestyle{plain}
  \addcontentsline{toc}{chapter}{#1}
  {\parindent=0pt
   \baselineskip=0pt
   \parskip=0pt
\vbox{
  \hbox to\textwidth {\hrulefill}
  \vbox to 3pt{ }
  \hbox to\textwidth {\hfill{\large\textsc{#1} \ %
   }}
  \vbox to 3pt{ }
  \hbox to\textwidth {\hrulefill}
  }}\par
  }

%% CAPTIONS FOR TABLES AND FIGURES
%%
%%  There's a new logical variable \tablecap, which is
%%  set \true by saying \tablecaptrue and \false by
%%  \tablecapfalse. The variable is expanded by saying
%%  \iftablecap. Then there are two separate \caption
%%  macros: \tabcaption and \figcaption, the definition
%%  of which are obvious. The \iftablecap is performed in
%%  \@makecaption, which now contains two different
%%  captioning styles.
%%                               J. Kaipio 3.10.1990.
%%
%%  A wider version with \small fonts, J. Kaipio 13.6.1995
%%
\newif\iftablecap
\def\tabcaption#1{\tablecaptrue\caption{#1}}
\def\figcaption#1{\tablecapfalse\caption{#1}}
\newlength{\t@bindwidth} \setlength{\t@bindwidth}{1cm}
\newlength{\c@pwidth} \setlength{\c@pwidth}{\hsize}
\addtolength{\c@pwidth}{-2\t@bindwidth}

\long\def\@makecaption#1#2{
   \vskip 10pt
   \iftablecap                           % Is it a table?
     \setbox\@tempboxa\hbox{#2}
     \ifdim \wd\@tempboxa > \c@pwidth      % IF longer than one line-2cm:
         \hbox to\hsize{\hfil{\sc #1}\hfil}
         \begin{list}{}{\leftmargin\t@bindwidth
             \rightmargin\t@bindwidth}
             {\item \footnotesize  #2}
         \end{list}  
     \else                               % ELSE  center.
         \hbox to\hsize{\hfil{\sc #1}\hfil}
         \hbox to\hsize{\hfil{\footnotesize #2}\hfil}
                        \vskip0.67\baselineskip\vfill
     \fi                                   % of \ifdim
   \else                                 % Not a table: a picture
     \setbox\@tempboxa\hbox{\small{\bf #1}: #2}
     \ifdim \wd\@tempboxa >1.2\c@pwidth       % IF longer than one line-2cm:
        \begin{list}{}{\leftmargin\t@bindwidth
           \rightmargin\t@bindwidth}
           {\small \item {\bf #1}: #2}
         \end{list}                        % THEN set as ordinary paragraph.
     \else                               % ELSE  center.
         \hbox to\hsize{\hfil\box\@tempboxa\hfil}
     \fi                                   % of \ifdim
   \fi                                   % of \if\tablecaptrue
   }                                     % \@makecaption

%  End of \@makecaption modifications.
